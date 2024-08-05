from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Teacher, Student, Administrator, Subject, SchoolYear, Class, GradingPeriod, GradingCriterion, Score, SubjectCriterion, Enrollment, Activity, Grade

class CustomUserAdmin(BaseUserAdmin):
    model = User
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_teacher', 'is_student', 'is_administrator')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'is_teacher', 'is_student', 'is_administrator')}
        ),
    )
    list_display = ('email', 'is_active', 'is_staff', 'is_superuser', 'is_teacher', 'is_student', 'is_administrator')
    search_fields = ('email',)
    ordering = ('email',)

# Register your models here
admin.site.register(User, CustomUserAdmin)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Administrator)
admin.site.register(Subject)
admin.site.register(SchoolYear)
admin.site.register(Class)



admin.site.register(GradingPeriod)
admin.site.register(SubjectCriterion)
admin.site.register(GradingCriterion)
admin.site.register(Score)
admin.site.register(Grade)
admin.site.register(Enrollment)
admin.site.register(Activity)
# admin.site.register(ClassSubject)


