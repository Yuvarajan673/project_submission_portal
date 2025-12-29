from datetime import date, datetime
import calendar
import math
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
# Redirecting the request to corresponding dashboard
def check_redirection(request):
    if request.user.role == 'admin' and request.path != '/dashboard/admin/':
        return redirect('/dashboard/admin/')
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


# Generate OTP and sends it to given email.
# And also creates the sessions to the request,
# that contain email, OTP and OTP created time.
def send_otp_to_email(request,email):
    otp=random.randint(100000,999999)
    request.session['otp']=otp
    request.session['user_email']=email
    request.session['otp_created_time']=time.time()
    subject= "Verify Your Email Address"
    message=f"Use the verification code below to complete your registration.\n\n {otp} \n\n It will expire in 5 minutes."
    from_email="submittly.noreply@gmail.com"
    send_mail(subject,message,from_email,[email])





# Generates Attributes for Calendar Layout
def generate_calendar(year,month):
    cal = calendar.Calendar() # Creating the cal Object
    month_days = cal.monthdayscalendar(year,month) # Getting the month days

    calendar_attrs = {
        'month_days':month_days, # Gives the dates of selected month to generate calendar dates
        'month':calendar.month_name[month], # Gives month name to check in the select tag
        'year':year,
    }
    return calendar_attrs





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
        send_otp_to_email(request,email)
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




# Profile page Views
@login_required
def user_profile(request,user_id):
    return render(request,'profile.html')


def upload_profile_image(request): 
    if request.method == 'POST' and request.FILES.get('profile-image'):
        if User.objects.get(id=request.user.id).profile_image:
            filepath = User.objects.get(id=request.user.id).profile_image.path
            if os.path.exists(filepath):
                os.remove(filepath)
        request.user.profile_image = request.FILES.get('profile-image')
        request.user.save()
        messages.success(request,"Profile Image Updated Successfully")
    return redirect(f"{request.META['HTTP_REFERER']}")


def remove_profile_image(request):
    filepath = User.objects.get(id=request.user.id).profile_image.path
    if os.path.exists(filepath):
        os.remove(filepath)
        User.objects.get(id=request.user.id).profile_image.delete()
        messages.success(request,"Profile Image Removed Successfully")
    return redirect(f"{request.META['HTTP_REFERER']}")


def update_first_and_last_name(request):
    if request.method == 'POST':
        data = {key:value for key,value in request.POST.items() if key != 'csrfmiddlewaretoken'}
        User.objects.filter(id=request.user.id).update(**data)
        messages.success(request,"Profile Name Updated Successfully")
    return redirect(f"{request.META['HTTP_REFERER']}")















""" 
===============================================
Student Dashboard
=============================================== 
"""

@login_required(login_url='/error/403/')
def student_dashboard(request):
    if check_redirection(request):
        return check_redirection(request)
    projects=Project.objects.filter(section=request.user.section).order_by('-created_at')

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

    for pro in projects:
        if Submission.objects.filter(submitted_by=request.user,submitted_to=pro).exists():
            project_status[pro.id]="submitted"
        elif not Submission.objects.filter(submitted_by=request.user,submitted_to=pro).exists() and pro.deadline >= timezone.now():
            project_status[pro.id]="pending"
        elif not Submission.objects.filter(submitted_by=request.user,submitted_to=pro).exists() and pro.deadline < timezone.now():
            project_status[pro.id]="missed"    

    return render(request,'student_dashboard.html',{
        'projects':projects,
        "project_status":project_status,
        'submission_count':submission_count,
        'pending_projects':projects.count()-missed_projects-submission_count,
        'missed_projects':missed_projects})



# Project Views
def get_all_projects(request):
    projects = Project.objects.filter(section=request.user.section)
    project_status = {}
    for pro in projects:
        if Submission.objects.filter(submitted_by=request.user,submitted_to=pro).exists():
            project_status[pro.id]="submitted"
        elif not Submission.objects.filter(submitted_by=request.user,submitted_to=pro).exists() and pro.deadline >= timezone.now():
            project_status[pro.id]="pending"
        elif not Submission.objects.filter(submitted_by=request.user,submitted_to=pro).exists() and pro.deadline < timezone.now():
            project_status[pro.id]="missed"

    return render(request,"student_layouts/projects.html",{'projects':projects,'project_status':project_status,'filter_by':'all'})



def filter_projects(request):
    filter_by = request.GET.get('filter-by', 'all')
    projects = Project.objects.filter(section=request.user.section)
    project_status = {}
    for pro in projects:
        if Submission.objects.filter(submitted_by=request.user,submitted_to=pro).exists():
            project_status[pro.id]="submitted"
        elif not Submission.objects.filter(submitted_by=request.user,submitted_to=pro).exists() and pro.deadline >= timezone.now():
            project_status[pro.id]="pending"
        elif not Submission.objects.filter(submitted_by=request.user,submitted_to=pro).exists() and pro.deadline < timezone.now():
            project_status[pro.id]="missed"

    # Filtering Submitted Projects
    if filter_by == "submitted":
        # Start from Project
        # Look for Submission objects linked to that Project
        # From those submissions, check:
        projects = projects.filter(submission__submitted_by=request.user)
    
    # Filtering Pending Projects
    elif filter_by == "pending":   # gte = Greater Than or Equal
        projects = projects.filter(deadline__gte=timezone.now()).exclude(submission__submitted_by=request.user)

    # Filtering Missed Projects
    elif filter_by == "missed":    # lt = Less Than
        projects = projects.filter(deadline__lt=timezone.now()).exclude(submission__submitted_by=request.user)
    return render(request,"student_layouts/projects.html",{'projects':projects,'project_status':project_status,'filter_by':filter_by})



def project_details(request,project_id):
    project=Project.objects.get(id=project_id)
    feedbacks=None
    reviewed=False
    if Submission.objects.filter(submitted_by=request.user,submitted_to=project_id).exists():
        feedbacks=Feedback.objects.filter(submission_id=Submission.objects.filter(submitted_by=request.user,submitted_to=project_id).first())
        submission=Submission.objects.filter(submitted_by=request.user,submitted_to=project_id).first()
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
    tot_students=User.objects.filter(role='student',section=request.user.section).count()
    not_reviewed=Submission.objects.filter(submitted_to=project_id,status='pending review').count()
    return render(request,'coach_layouts/submissions.html',{
        'submissions':submissions,
        'project':project,
        'total_students':tot_students,
        'submitted_students':submissions.count(),
        'pending_students':tot_students-submissions.count(),
        'not_reviewed':not_reviewed})
    




def del_mysub(request,p_id):
    prev_url=request.META.get('HTTP_REFERER')
    Submission.objects.filter(submitted_by=request.user,submitted_to=p_id).delete()
    messages.success(request,"Your Submission Deleted Successfully")
    return redirect(prev_url)








""" 
===============================================
Coach Dashboard
=============================================== 
"""

@login_required(login_url='/error/403/')
def coach_dashboard(request):
    if check_redirection(request):
        return check_redirection(request)
    
    

    # Count the attendance for today
    attendance_for_today = {
        'present':Attendance.objects.filter(student__section=request.user.section,status='present',date=date.today()).count(),
        'absent':Attendance.objects.filter(student__section=request.user.section,status='absent',date=date.today()).count(),
        'late':Attendance.objects.filter(student__section=request.user.section,status='late',date=date.today()).count()
    }

    projects=Project.objects.filter(created_by=request.user)
    # Project Status
    project_status=[]
    for pro in projects:
        if not Submission.objects.filter(submitted_to=pro.id).exists():
            project_status.append(pro.id)
    sub_count={}
    tot_student=User.objects.filter(role='student',section=request.user.section).count()
    for pro in projects:
        sub_count[pro.id]=Submission.objects.filter(submitted_to=pro).count()
    return render(request,'coach_dashboard.html',{'projects':projects,'sub_count':sub_count,'tot_student':tot_student,'attendance_for_today':attendance_for_today,'project_status':project_status})




def attendance(request):
    students = User.objects.filter(section=request.user.section,role='student').order_by('first_name')
    today_att = {rcd.student.id:rcd.status for rcd in Attendance.objects.filter(student__section=request.user.section,date=timezone.now())}
    if today_att == {}:
        today_att=False
    print(today_att)
    return render(request,"coach_layouts/attendance.html",{'students':students,'sec':request.user.section,'today_att':today_att})



def attendance_report(request):
    # Getting the form data from the request
    year = int(request.GET.get("year", date.today().year))
    month = int(request.GET.get("month", date.today().month))
    student = int(request.GET.get("student", User.objects.filter(section=request.user.section,role='student').order_by('first_name').first().id))

    # Genarating the calendar
    calendar_attrs = generate_calendar(year,month)

    # Getting the attendance for selected month and year for selected student 
    attendance_records = Attendance.objects.filter(student_id=student,date__year=year,date__month=month)
    # Mapping the date and attendance eg:{31:present,...}
    attendance_map = {rcd.date.day:rcd.status for rcd in attendance_records}
    attendance = 0
    if attendance_records.count() != 0:
        attendance = math.floor((attendance_records.filter(status='present').count()/attendance_records.count())*100)

    att_summary = {
        'present':attendance_records.filter(status='present').count(),
        'absent':attendance_records.filter(status='absent').count(),
        'late':attendance_records.filter(status='late').count(),
        'attendance':attendance
    }
    # Hardcoded data of month and year
    years = [2023,2024,2025,2026]
    months = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
    } 
    
    students = User.objects.filter(section=request.user.section,role='student').order_by('first_name')
    return render(request,"coach_layouts/attendance_report.html",{
        'calendar_attrs':calendar_attrs,
        'months':months, # Gives the list of months to show in the select tag's option
        'years':years, # Gives the list of years to show in the select tag's option
        'students':students, # Gives the list of students to show in the select tag's option
        'attendance_map':attendance_map, # Mapped attendance date to mark calendar
        'student':User.objects.get(id=student), # Gives the student name to check in select tag
        'att_summary':att_summary}) # Gives the year to check in the select tag



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
            Project.objects.create(created_by=request.user,section=request.user.section,**data)
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



def all_sections(request):
    sections={}
    for sec in User._meta.get_field("section").choices:
        sections[sec[0]]={
            "tot_stu":User.objects.filter(role='student',section=sec[0]).count(),
            "pres":Attendance.objects.filter(student__section=sec[0],status='present',date=date.today()).count(),
            "abs":Attendance.objects.filter(student__section=sec[0],status='absent',date=date.today()).count(),
            "late":Attendance.objects.filter(student__section=sec[0],status='late',date=date.today()).count()
            }
    return render(request,"admin_layouts/all_sections.html",{'sections':sections})




def get_sec_students(request,sec):
    students=User.objects.filter(section=sec,role="student").order_by("username")
    today_att={i.student.id:i.status for i in Attendance.objects.filter(student__section=sec,date=date.today())}
    if today_att == {}: 
        today_att=False
    return render(request,"admin_layouts/section.html",{"students":students,"sec":sec,"today_att":today_att})



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