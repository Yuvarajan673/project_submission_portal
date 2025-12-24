from datetime import date, datetime
import time, random
from django.shortcuts import *
from .models import *
from django.core.mail import send_mail
from django.apps import apps
from django.contrib.auth.decorators import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout


# Create your views here.



#CUSTOM FUNCTIONS
def check_redirection(request):
    if request.user.role == 'admin' and request.path != '/dashboard/admin':
        return redirect('/dashboard/admin')
    elif request.user.role == 'coach' and request.path != '/dashboard/coach/':
        return redirect('/dashboard/coach/')
    elif request.user.role == 'student' and request.path != '/dashboard/student/':
        return redirect('/dashboard/student/')
    return None



def order_fields(flds,custom_fields=[
        ['first_name','last_name','username','section','email','role','date_joined','last_login'],
        ['title','description','deadline','created_by','created_at'],
        ['submitted_by','submitted_to','submitted_at']
        ]):
    
    ordered_fields=[]
    for i in range(len(custom_fields)):
        for j in range(len(custom_fields[i])):
            if custom_fields[i][j] in flds:
                ordered_fields.append(custom_fields[i][j])
        
    return ordered_fields

def get_own_fields(fields,custom_fields):
    cus_fld=[]
    for i in custom_fields:
        if i in fields:
            cus_fld.append(i)
    return cus_fld


def get_fields(model):
    fields=[]
    for f in model._meta.fields:
        fields.append(f.name)
    return fields






#vIEW FUNCTIONS
def home(request):
    if request.user.is_authenticated and check_redirection(request):
        return check_redirection(request)
    return render(request,"home.html")





def login_user(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username=request.POST.get('username').strip()
        pwd=request.POST.get('password').strip()

        context={
            'uname':username,
            'pwd':pwd
        }

        user = authenticate(request,username=username,password=pwd)
        if user is not None:
            login(request,user)
            if user.role=='admin':
                messages.success(request,"Logged in as Admin Successfully")
                return redirect('/dashboard/admin/')
            if user.role == 'coach':
                messages.success(request,"Logged in as Coach Successfully")
                return redirect('/dashboard/coach/')
            if user.role == 'student':
                messages.success(request,"Logged in as Student Successfully")
                return redirect('/dashboard/student/')
            
        messages.error(request, "* Please enter the correct ussername or password")
        return render(request,'login.html',context)
    return render(request,'login.html')





def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged out Successfully")
    return redirect('/')




def send_otp(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method=='POST':
        email=request.POST.get('email').strip()
        
        otp=random.randint(100000,999999)

        request.session['otp']=otp
        request.session['user_email']=email
        request.session['otp_created_time']=time.time()

        subject= "Verify Your Email Address"
        message=f"Use the verification code below to complete your registration.\n\n {otp} \n\n It will expire in 5 minutes."
        from_email="submittly.noreply@gmail.com"
        send_mail(subject,message,from_email,[email])
        messages.success(request, "Verification Code Sent To your Email")
        return redirect('/verify/')

    return render(request,"send_otp.html")



def verify(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method=='POST':
        verify_otp=request.POST.get('verify-code').strip()
        saved_otp = request.session.get('otp')
        created_time=request.session.get('otp_created_time')

        context={
            'otp':verify_otp
        }

        if created_time and time.time()-created_time > 300:
            del request.session['otp']
            del request.session['otp_created_time']
            return messages.error(request,"* OTP expired")
            
        elif str(verify_otp) == str(saved_otp):
            del request.session['otp']
            del request.session['otp_created_time']
            return redirect('/register/')
        
        else:
            messages.error(request,"* Enter Valid OTP")
            return render(request,'verify.html',context)
        
    return render(request,'verify.html')



def register(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method=='POST':
        firstname=request.POST.get('firstname').strip()
        lastname=request.POST.get('lastname').strip()
        username=request.POST.get('username').strip()
        pwd=request.POST.get('password1').strip()
        con_pwd=request.POST.get('password2').strip()
        role=request.POST.get('user-role')
        email=request.session.get('user_email')

        context={
            'fname':firstname,
            'lname':lastname,
            'uname':username,
            'pwd':pwd,
            'con_pwd':con_pwd,
            'role':role
        }
        
        if User.objects.filter(username=username).exists():
            messages.error(request,'* Username already taken')
            return render(request,'register.html',context)
        if pwd==con_pwd:
            User.objects.create_user(
                first_name=firstname,
                last_name=lastname,
                username=username,
                email=email,
                password=pwd,
                role=role)
            messages.success(request, "Your Account Created Successfuly")
            return render(request,"login.html")
        else:
            messages.error(request,"* Passwords didn't match")
            return render(request,'register.html',context)
    return render(request,'register.html')


@login_required(login_url='/error/403/')
def student_dashboard(request):
    if check_redirection(request):
        return check_redirection(request)
    projects=Project.objects.all().order_by('-created_at')

    # Count the Missed Project
    missed_projects = 0
    submitted_project_ids = Submission.objects.filter(submitted_by=request.user).values_list('submitted_to_id', flat=True)
    for project in projects:
        if project.deadline < timezone.now() and project.id not in submitted_project_ids:
            missed_projects += 1
    # Count the Submissions
    submission_count=0
    if Submission.objects.filter(submitted_by=request.user).exists():
        submission_count=Submission.objects.filter(submitted_by=request.user).count()

    # Fetching the Project Status
    project_status={}
    for project in projects:
        project_status[project.id]={"submitted":Submission.objects.filter(submitted_to=project,submitted_by=request.user).exists()}
    return render(request,'student_dashboard.html',{
        'projects':projects,
        "project_status":project_status,
        'submission_count':submission_count,
        'pending_projects':projects.count()-missed_projects-submission_count,
        'missed_projects':missed_projects})



def project_details(request,project_id):
    project=Project.objects.get(id=project_id)
    feedbacks=None
    reviewed=False
    if Submission.objects.filter(submitted_by=request.user,submitted_to=project_id).exists():
        feedbacks=Feedback.objects.filter(submission_id=Submission.objects.get(submitted_by=request.user,submitted_to=project_id))
        submission=Submission.objects.get(submitted_by=request.user,submitted_to=project_id)
        if submission.grade != None or submission.status != 'pending review':
            reviewed=True
    answer_submitted=False
    if Submission.objects.filter(submitted_by=request.user,submitted_to=project_id).exists():
        answer_submitted=True
    return render(request,'student_layouts/project_details.html',{'project':project,'feedbacks':feedbacks,'answer_submitted':answer_submitted,'reviewed':reviewed})
    


def submit_answer(request,project_id):
    if request.method=='POST':
        post_data={key:value for key,value in request.POST.items() if key != 'csrfmiddlewaretoken'}
        if not post_data['file_path']:
            del post_data['file_path']
        Submission.objects.create(submitted_by=request.user,submitted_to_id=project_id,**post_data)
        messages.success(request,"Answer Submitted Successfully")
    return redirect(f"{request.META['HTTP_REFERER']}")


def view_submissions(request,project_id):
    project=Project.objects.get(id=project_id)
    submissions=Submission.objects.filter(submitted_to_id=project_id)
    return render(request,'coach_layouts/submissions.html',{'submissions':submissions,'project':project})
    




def del_mysub(request,p_id):
    prev_url=request.META.get('HTTP_REFERER')
    Submission.objects.filter(submitted_by=request.user,submitted_to=p_id).delete()
    messages.success(request,"Your Submission Deleted Successfully")
    return redirect(prev_url)



@login_required(login_url='/error/403/')
def coach_dashboard(request):
    if check_redirection(request):
        return check_redirection(request)
    sections={}
    for sec in User._meta.get_field("section").choices:
        sections[sec[0]]={
            "tot_stu":User.objects.filter(section=sec[0]).count(),
            "pres":Attendance.objects.filter(student__section=sec[0],status='present',date=date.today()).count(),
            "abs":Attendance.objects.filter(student__section=sec[0],status='absent',date=date.today()).count(),
            "late":Attendance.objects.filter(student__section=sec[0],status='late',date=date.today()).count()
            }
    projects=Project.objects.filter(created_by=request.user)
    sub_count={}
    tot_student=User.objects.filter(role='student').count()
    for pro in projects:
        sub_count[pro.id]=Submission.objects.filter(submitted_to=pro).count()
    return render(request,'coach_dashboard.html',{'projects':projects,'sub_count':sub_count,'tot_student':tot_student,'sections':sections})



def submission_details(request,sub_id):
    submission = None
    if Submission.objects.filter(id=sub_id).exists():
        submission=Submission.objects.get(id=sub_id)
    else:
        messages.error(request,"Submission Doesn't Exist")
        return redirect(f"{request.META['HTTP_REFERER']}")
    feedbacks = Feedback.objects.filter(submission_id_id=sub_id)
    return render(request,"coach_layouts/submission_details.html",{"submission":submission,"feedbacks":feedbacks})



def save_grade(request,sub_id):
    if request.method == "POST":
        Submission.objects.filter(id=sub_id).update(grade=request.POST['grade'],status="reviewed")
        messages.success(request,"Graded Successfully")
    return redirect(f"{request.META["HTTP_REFERER"]}")



def save_feedback(request,sub_id):
    feedback_msg=request.POST['feedback']
    Feedback.objects.create(
        submission_id_id=sub_id,
        feedback=feedback_msg
    )
    messages.success(request,"Feedback Posted Successfully")
    return redirect(f"{request.META['HTTP_REFERER']}")



def get_sec_students(request,sec):
    students=User.objects.filter(section=sec,role="student").order_by("username")
    today_att={i.student.id:i.status for i in Attendance.objects.filter(student__section=sec,date=date.today())}
    if today_att == {}: 
        today_att=False
    return render(request,"coach_layouts/section.html",{"students":students,"sec":sec,"today_att":today_att})


def save_attendance(request,sec):
    students=User.objects.filter(section=sec,role="student").order_by("username")
    if request.method=='POST':
        attendance={int(k):v for k,v in request.POST.items() if k != "csrfmiddlewaretoken"}
        for student in students:
            status=attendance[student.id]
            if status:
                Attendance.objects.create(
                    student=student,
                    status=status,
                    marked_by=request.user
                )
        messages.success(request,"Attendance Marked Successfully")
        
    return redirect(f"{request.META["HTTP_REFERER"]}")



def create_project(request):
    if request.method=='POST':
        data={key:val for key,val in request.POST.items() if key != 'csrfmiddlewaretoken'}
        if data['action']=='cancel':
            return redirect('/dashboard/coach/')
        if data['action']=='createproject':
            if data['file_path']=="":
                del data['file_path']
            del data['action']
            Project.objects.create(created_by=request.user,**data)
            messages.success(request,"Your Project Created Successfully")
            return redirect('/dashboard/coach/')
        if data['action']=='save':
            if data['file_path']=="":
                del data['file_path']
            del data['action']
            Project.objects.filter(id=request.POST['id']).update(**data)
            messages.success(request,"Your Project Updated Successfully")
            return redirect('/dashboard/coach/')
            
    return render(request,"coach_layouts/create_project.html")




def edit_project(request,project_id):
    project=Project.objects.get(id=project_id)
    project_data={}
    for i in project._meta.fields:
        project_data[i.name]=getattr(project,i.name)
    project_data['deadline']=datetime.strftime(project_data['deadline'],'%Y-%m-%dT%H:%M')
    return render(request,"coach_layouts/create_project.html",{"project":project_data})



def delete_project(request,project_id):
    Project.objects.get(id=project_id).delete()
    messages.success(request,"Your Project Deleted Successfully")
    return redirect(f"{request.META['HTTP_REFERER']}")
    



def edit_or_delete_project(request,project_id):
    if request.GET['action']=='delete':
        Project.objects.get(id=project_id).delete()
        messages.success(request,"Your Project Deleted Successfully")
    if request.GET['action']=='edit':
        project=Project.objects.get(id=project_id)
        fields=['id','title','description','deadline','document_link']
        data={}
        for field in fields:
            data[field]=getattr(project,field)
        data['deadline']=datetime.strftime(data['deadline'],'%Y-%m-%dT%H:%M')
        return render(request,"coach_layouts/create_project.html",{'project':data})
    return redirect('/')



@login_required(login_url='/login/')
def admin_dashboard(request):
    if check_redirection(request):
        return check_redirection(request)
    
    app_config=apps.get_app_config('submittly')
    app_models=app_config.get_models()

    model_list=[]

    for model in app_models:
        model_list.append({
            'name':model.__name__,
            'count':model.objects.count()
        })

    return render(request,'admin_dashboard.html',{'models':model_list})




def table_filter(request,mod_name):
    role = request.GET.get('filter-role')
    model=apps.get_model('submittly',mod_name)
    fields=order_fields(get_fields(model))
    users=model.objects.all()
    if role:
        users=model.objects.filter(role=role)
    return render(request,'admin_dashboard.html',{'users':users,'fields':fields,'role':role,'mod_name':mod_name,'show_table':True})



 
@login_required(login_url='/login/')
def model_details(request,mod_name):
    model=apps.get_model('submittly',mod_name) 
    fields=get_fields(model)
    fields=order_fields(fields)
    users=model.objects.all()
    return render(request,'admin_dashboard.html',{'users':users,'fields':fields,'mod_name':mod_name,'show_table':True})



@login_required(login_url='/login/')
def change_user(request,id,mod_name):
    model=apps.get_model('submittly',mod_name)
    user=model.objects.get(id=id)
    getfields=get_fields(model)
    custom_fields=['first_name','last_name','username','email','role','date_joined','last_login','is_superuser','is_staff','is_active']
    fields=get_own_fields(getfields,custom_fields=custom_fields)
    data={'id':id,
          'mod_name':mod_name, 
          'show_template':False}
    for f in fields:
        data[f]=getattr(user,f)
    data['date_joined']=datetime.strftime(data['date_joined'],'%Y-%m-%dT%H:%M')
    if data['last_login']:
        data['last_login']=datetime.strftime(data['last_login'],'%Y-%m-%dT%H:%M')
    else:
        data['last_login']=None
    if user:
        data['show_template']=True
    return render(request,'admin_dashboard.html',{'data':data})





@login_required(login_url='/error/403/')
def add_user(request,mod_name):
    btn_value=request.GET.get('mode')
    data={'id':request.user.id,
          'show':False,
          'mod_name':mod_name}
    if btn_value=='adduser':
        data['show']=True 
    return render(request,'admin_dashboard.html',{'data':data})





@login_required(login_url='/error/403/')
def adminform(request,id,mod_name):
    if request.method=='POST':
        model=apps.get_model('submittly',mod_name)
        data = {key:value for key,value in request.POST.items() if key != 'csrfmiddlewaretoken'}

        data['date_joined']=datetime.strptime(data['date_joined'],'%Y-%m-%dT%H:%M')
        if data['last_login']:
            data['last_login']=datetime.strptime(data['last_login'],'%Y-%m-%dT%H:%M')
        if data['last_login']=='':
            data['last_login']=None
        
        if data['action'] =='change':
            data.pop('action')
            model.objects.filter(id=id).update(**data)
            messages.success(request,"Changed Successfully")
        elif data['action']=='add':
            data.pop('action')
            model.objects.create_user(**data)
            messages.success(request,"Added Successfully")
        elif data['action']=='delete':
            model.objects.get(id=id).delete()
            messages.success(request,"Deleted Successfully")
        return redirect(f'/model_details/{mod_name}')

    return render(request,'admin_dashboard.html')





def error_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    return render(request,'403.html',status=403)








# def view_sub_or_details(request):
#     project=Project.objects.get(id=request.GET['id'])
#     prev_url=request.META.get('HTTP_REFERER')
#     submissions = Submission.objects.filter(submitted_to=request.GET['id']).order_by('-submitted_at')
#     curnt_user_submission=Submission.objects.filter(submitted_by=request.user,submitted_to=request.GET['id']).first()
#     if request.method=='POST':
#         if "submit_answer" in request.POST:
#             data={k:v for k,v in request.POST.items() if k !='csrfmiddlewaretoken'}
#             if not data['file_path']:
#                 del data['file_path']
#             user=User.objects.get(id=request.user.id)
#             project=Project.objects.get(id=data['submitted_to'])
#             Submission.objects.create(submitted_by=user,submitted_to=project,ans_doc_link=data['ans_doc_link'])
#             messages.success(request,"Answer Submitted Successfully")
#         return redirect(prev_url)
#     if request.GET['action']=='viewdetails':
#         feedbacks=Feedback.objects.filter(submission_id=curnt_user_submission)
#         return render(request,'student_layouts/project_details.html',{'submissions':submissions,'feedbacks':feedbacks,'project':project,'ans_submitted':curnt_user_submission})
#     if request.GET['action']=='viewsubmission':
#         return render(request,'coach_layouts/submissions.html',{'submissions':submissions,'project':project})
#     return redirect('/dashboard/student/')