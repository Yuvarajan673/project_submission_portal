from django.contrib import admin
from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display=('username','first_name','section','role','email','date_joined')

class ProjectAdmin(admin.ModelAdmin):
    list_display=('title','description','deadline','created_by','created_at')

class SubmissionAdmin(admin.ModelAdmin):
    list_display=('submitted_to','submitted_by')

class AttendanceAdmin(admin.ModelAdmin):
    list_display=('student','status','marked_by','date')

# Register your models here.
admin.site.register(User,UserAdmin)
admin.site.register(Project,ProjectAdmin)
admin.site.register(Submission,SubmissionAdmin)
admin.site.register(Attendance,AttendanceAdmin)