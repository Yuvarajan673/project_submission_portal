import os
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser



def getFilePath(instance,filename):
    extension = os.path.splitext(filename)[1] #It gives the extension of the file eg: .png .jpg or .jpeg
    return f"profile_images/{instance.username}{extension}"


SECTION_CHOICE=[
        ("A","A"),
        ("B","B"),
        ("C","C")
    ]
# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES=[
        ("student","Student"),
        ("coach","Coach"),
        ("admin","Admin")
    ]
    
    role=models.CharField(max_length=15,choices=ROLE_CHOICES)
    section=models.CharField(max_length=1,choices=SECTION_CHOICE,blank=True,null=True)
    profile_image=models.ImageField(upload_to=getFilePath,blank=True,null=True)

class Project(models.Model):
    title=models.CharField(max_length=255)
    description=models.TextField()
    deadline=models.DateTimeField(null=True)
    document_link=models.URLField(blank=True)
    created_by=models.ForeignKey(User,on_delete=models.CASCADE,limit_choices_to={'role':'coach'})
    created_at=models.DateTimeField(default=timezone.now)
    section = models.CharField(max_length=5,choices=SECTION_CHOICE,null=True)

    def __str__(self):
        return self.title
    
class Submission(models.Model):
    STATUS=[
        ('pending review','Pending Review'),
        ('reviewed','Reviewed')
    ]
    GRADE=[
        ('excellent','Excellent'),
        ('good','Good'),
        ('average','Average'),
        ('poor','Poor')
    ]
    submitted_by=models.ForeignKey(User,on_delete=models.CASCADE,limit_choices_to={'role':'student'})
    submitted_to=models.ForeignKey(Project,on_delete=models.CASCADE)
    ans_doc_link=models.URLField(blank=True)
    submitted_at=models.DateTimeField(default=timezone.now)
    status=models.CharField(max_length=20,choices=STATUS,default='pending review')
    grade=models.CharField(max_length=10,choices=GRADE,null=True,blank=True)

    def __str__(self):
        return self.submitted_to.title
    
class Attendance(models.Model):
    STATUS_CHOICE=[
        ("present","Present"),
        ("absent","Absent"),
        ("late","Late")
    ]
    student=models.ForeignKey(User,on_delete=models.CASCADE)
    status=models.CharField(max_length=10,choices=STATUS_CHOICE)
    date=models.DateField(auto_now_add=True)
    marked_by=models.ForeignKey(User,related_name="marked_attendance",limit_choices_to={'role':'coach'},on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return f"{self.student} : {self.status}"
        

class Feedback(models.Model):
    submission_id=models.ForeignKey(Submission,on_delete=models.CASCADE)
    feedback=models.TextField()
    posted_date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Project:{self.submission_id.submitted_to.title}, Student:{self.submission_id.submitted_by.first_name}"
    
    