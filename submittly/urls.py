from django.urls import path
from . import views,models

urlpatterns=[
    # Home Route
    path('',views.home,name='home'),


    # Auth Routes
    path('login/',views.login_user,name='login_user'),
    path('logout/',views.logout_user,name='logout_user'),
    path('send/otp',views.send_otp,name='send_otp'),
    path('verify/',views.verify,name='verify'),
    path('register/',views.register,name='register'),

    
    # Error Page Route
    path('error/403/',views.error_page,name='error_page'),



    # Student Dashboard Routes
    path('dashboard/student/',views.student_dashboard,name='student_dashboard'),
    path('project/details/<int:project_id>',views.project_details,name='project_details'),
    path('answer/submit/<int:project_id>',views.submit_answer,name='submit_answer'),
    path('delete/submission/<int:p_id>/',views.del_mysub,name='del_mysub'),



    # Coach Dashboard Routes
    path('dashboard/coach/',views.coach_dashboard,name='coach_dashboard'),
    path('create/project/',views.create_project,name='create_project'),
    path('section/<str:sec>/students/',views.get_sec_students,name='get_sec_students'),
    path('attendance/save/<str:sec>/',views.save_attendance,name='save_attendance'),
    path('view/submissions/<int:project_id>/',views.view_submissions,name='view_submissions'),
    path('submission/details/<int:sub_id>/',views.submission_details,name='submission_details'),
    path('grade/save/<int:sub_id>/',views.save_grade,name='save_grade'),
    path('feedback/save/<int:sub_id>/',views.save_feedback,name='save_feedback'),
    path('edit/project/<int:project_id>/',views.edit_project,name='edit_project'), 
    path('delete/project/<int:project_id>/',views.delete_project,name='delete_project'), 
   
    
    # todo seperate views
    # path('edit_or_delete_project/<int:project_id>/',views.edit_or_delete_project,name='edit_or_delete_project'), 
    # path('view_sub_or_details/',views.view_sub_or_details,name='view_sub_or_details'),




    # Admin Dashboard Routes
    path('dashboard/admin',views.admin_dashboard,name='admin_dashboard'),
    path('table_filter/<str:mod_name>/',views.table_filter,name='table_filter'),
    path('add_user/<str:mod_name>/',views.add_user,name='add_user'),
    path('adminform/<int:id>/<str:mod_name>/',views.adminform,name='adminform'),
    path('model_details/<str:mod_name>/',views.model_details,name='model_details'),
    path('change_user/<int:id>/<str:mod_name>/',views.change_user,name='change_user'),
]