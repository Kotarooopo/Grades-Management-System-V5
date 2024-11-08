from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView



urlpatterns = [
    path('login/', views.login, name='login'),
    path('admin-dashboard/', views.dashboard, name = 'admin-dashboard'),
    path('admin-profile/', views.profile, name = 'admin-profile'),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.register_user, name='register'),
    path('teacher-list/', views.teacher_list, name='teacher-list'),
    path('student-list/', views.student_list, name='student-list'),
    path('administrator-list/', views.administrator_list, name='administrator-list'),
    path('administrator/school-year/', views.manage_school_year, name='admin-SY'),
    path('administrator/grading-period/', views.admin_GradingPeriod, name='admin-GradingPeriod'),
    path('administrator/admin-subject/', views.admin_subject, name='admin-subject'),
    path('administrator/SubjectCriteria/', views.subject_criteria, name='subject-criteria'),
    path('get-subject-criteria/', views.get_subject_criteria, name='get_subject_criteria'),
    path('administrator/GradeReport/', views.admin_GradeReport, name='admin-GradeReport'),
    path('administrator/Class/PreviousClass', views.admin_prevClass, name ='admin-prevClass'),
    path('administrator/admin-class/', views.admin_class, name='admin-class'),

    path('update-score/', views.update_score, name='update_score'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher-dashboard'),
    path('teacher-profile/', views.teacher_profile, name = 'teacher-profile'),
    path('teacher-myClassAdvisory/', views.teacher_myClassAdvisory, name = 'teacher-myClassAdvisory'),
    path('teacher-prevClassAdvisory/', views.teacher_prevClassAdvisory, name = 'teacher-prevClassAdvisory'),
    path('teacher-myClassAdvisory/myClassRecord/', views.teacher_myClassRecord, name = 'teacher-myClassRecord'),
    path('teacher-myClassAdvisory/myGradeCalculation', views.teacher_gradeCalculate, name = 'teacher-mygradeCalculate'),
    path('remove-student/', views.remove_student, name='remove-student'),
    path('upload-grades/', views.upload_grades, name='upload-grades'),
    path('teacher-SummaryGrade', views.teacher_SummaryGrades, name='teacher-SummaryGrade'),
    path('teacher-SummaryGrade/teacher-QuarterSummary', views.teacher_QuarterSummary, name='teacher-QuarterSummary'),
    path('teacher-prevSummaryGrade', views.teacher_prevSummaryGrade, name='teacher-prevSummaryGrade'),


    path('student-dashboard/', views.student_dashboard, name='student-dashboard'),
    path('student-profile/', views.student_profile, name='student-profile'),
    path('student-SubjectList/', views.student_subjectlist, name='student-SubjectList'),
    path('student-ScoreList', views.student_scorelist, name='student-ScoreList'),
    path('student-reportCard/', views.student_reportCard, name='student-reportCard'),
    path('student-previousClasses', views.student_previousClasses, name='student-previousClasses'),
    path('student-InitialGrade', views.student_InitialGrade, name='student-InitialGrade'),
    
    



    path('api/get_scores/', views.get_scores, name='get_scores'),
    path('api/get_activity_details/<int:activity_id>/', views.get_activity_details, name='get_activity_details'),
    path('edit_activity/<int:activity_id>/', views.edit_activity, name='edit_activity'),
    path('delete-activity/', views.delete_activity, name='delete_activity'),
    path('change_student_password/', views.change_student_password, name='change_student_password'),
    path('teachers/change-password/', views.change_teacher_password, name='change_teacher_password'),
    path('delete-student/', views.delete_student, name='delete_student'),
    path('delete-teacher/', views.delete_teacher, name='delete_teacher'),
    path('api/class/<int:class_id>/toggle-scores/', views.toggle_scores, name='toggle_scores'),
    #path('export-report-card/', views.export_report_card, name='export-report-card'),



    

    
    
    
]