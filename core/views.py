from django.shortcuts import redirect, render
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

from django.contrib.auth.decorators import login_required

from .models import *
    
from .decorators import unauthenticated_user, allowed_users

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users
from django.views.decorators.http import require_GET
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import User, Class  
from django.http import JsonResponse

@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
def dashboard(request):
    total_teachers = User.objects.filter(is_teacher=True).count()
    total_students = User.objects.filter(is_student=True).count()
    total_administrators = User.objects.filter(is_administrator=True).count()
    total_users = User.objects.count()

    sections = Class.objects.values('grade_level', 'section').distinct()
    grade_sections = {}
    for section in sections:
        grade_level = section['grade_level']
        if grade_level not in grade_sections:
            grade_sections[grade_level] = 0
        grade_sections[grade_level] += 1

    total_sections = sum(grade_sections.values())

    grade_sections_with_percentage = {}
    for grade, count in grade_sections.items():
        percentage = (count / total_sections) * 100 if total_sections > 0 else 0
        grade_sections_with_percentage[grade] = {
            'count': count,
            'percentage': round(percentage, 1)
        }

    total_subjects = Subject.objects.count()
    subjects = Subject.objects.all()  

    
    current_school_year = SchoolYear.objects.filter(is_active=True).first()

    context = {
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_administrators': total_administrators,
        'total_users': total_users,
        'total_sections': total_sections,
        'total_subjects': total_subjects,
        'subjects': subjects,  
        'current_school_year': current_school_year, 
        'grade_sections': json.dumps(grade_sections),
        'grade_sections_with_percentage': grade_sections_with_percentage,
    }

    return render(request, 'admin-dashboard.html', context)










from django.http import JsonResponse
from .models import Subject, SubjectCriterion

def get_subject_criteria(request):
    subject_name = request.GET.get('subject')
    try:
        subject = Subject.objects.get(name=subject_name)
        criteria = SubjectCriterion.objects.filter(subject=subject)
        labels = [criterion.grading_criterion.get_criteria_type_display() for criterion in criteria]
        values = [criterion.weightage for criterion in criteria]
        return JsonResponse({'labels': labels, 'values': values})
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Subject not found'}, status=404)









@unauthenticated_user
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            if user.is_administrator:
                return JsonResponse({'success': True, 'redirect_url': '/admin-dashboard/'})
            elif user.is_teacher:
                return JsonResponse({'success': True, 'redirect_url': '/teacher-dashboard/'})
            elif user.is_student:
                return JsonResponse({'success': True, 'redirect_url': '/student-dashboard/'})
            else:
                return JsonResponse({'success': False, 'message': 'User role not defined.'})
        else:
            return JsonResponse({'success': False, 'message': 'Username or Password is incorrect'})

    # Handle GET request
    return render(request, 'login.html')



def logoutUser(request):
    logout(request)
    return redirect('login')



#edit-profile admin
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .forms import AdministratorForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
def profile(request):
    admin = request.user.administrator

    if request.method == 'POST':
        if 'current_password' in request.POST:
            change_form = PasswordChangeForm(request.POST)
            if change_form.is_valid():
                current_password = change_form.cleaned_data['current_password']
                new_password = change_form.cleaned_data['new_password']
                
                if not request.user.check_password(current_password):
                    return JsonResponse({'status': 'error', 'message': 'Current password is incorrect'})
                else:
                    user = request.user
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    return JsonResponse({'status': 'success', 'message': 'Your password was successfully updated!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid form data'})
        else:
            form = AdministratorForm(request.POST, request.FILES, instance=admin)
            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success', 'message': 'Profile updated successfully!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'There was an issue updating the profile'})
    
    # If not POST, fallback for GET
    form = AdministratorForm(instance=admin)
    change_form = PasswordChangeForm()

    context = {
        'form': form,
        'change_form': change_form,
        'administrator': admin,
    }
    return render(request, 'admin-profile.html', context)








#edit-profile teacher


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import TeacherForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


@login_required
@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def teacher_profile(request):
    teacher = request.user.teacher

    if request.method == 'POST':
        if 'current_password' in request.POST:
            change_form = PasswordChangeForm(request.POST)
            form = TeacherForm(instance=teacher)
            if change_form.is_valid():
                current_password = change_form.cleaned_data['current_password']
                new_password = change_form.cleaned_data['new_password']
                
                if not request.user.check_password(current_password):
                    return JsonResponse({'status': 'error', 'message': 'Current password is incorrect'})
                else:
                    user = request.user
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)  # Important!
                    return JsonResponse({'status': 'success', 'message': 'Your password was successfully updated!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid form data'})
                    
        else:
            form = TeacherForm(request.POST, request.FILES, instance=teacher)
            change_form = PasswordChangeForm()
            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success', 'message': 'Profile updated successfully!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'There was an issue updating the profile'})
    else:
        form = TeacherForm(instance=teacher)
        change_form = PasswordChangeForm()

    context = {
        'form': form,
        'change_form': change_form,
        'teacher': teacher,
    }
    return render(request, 'teacher-profile.html', context)



#edit-profile student


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import StudentForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
@login_required(login_url='login')
@allowed_users(allowed_roles=['student'])
def student_profile(request):
    student = request.user.student

    if request.method == 'POST':
        # Check if request is AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if 'current_password' in request.POST:
            change_form = PasswordChangeForm(request.POST)
            form = StudentForm(instance=student)
            if change_form.is_valid():
                current_password = change_form.cleaned_data['current_password']
                new_password = change_form.cleaned_data['new_password']
                
                if not request.user.check_password(current_password):
                    if is_ajax:
                        return JsonResponse({'status': 'error', 'message': 'Current password is incorrect'})
                    messages.error(request, 'Current password is incorrect')
                else:
                    user = request.user
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    if is_ajax:
                        return JsonResponse({'status': 'success', 'message': 'Your password was successfully updated!'})
                    messages.success(request, 'Your password was successfully updated!')
                    return redirect('student-profile')
            else:
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': 'Invalid form data'})
        else:
            form = StudentForm(request.POST, request.FILES, instance=student)
            change_form = PasswordChangeForm()
            if form.is_valid():
                form.save()
                if is_ajax:
                    return JsonResponse({'status': 'success', 'message': 'Profile updated successfully!'})
                messages.success(request, 'Profile updated successfully!')
                return redirect('student-profile')
            else:
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': 'There was an issue updating the profile'})
    else:
        form = StudentForm(instance=student)
        change_form = PasswordChangeForm()

    context = {
        'form': form,
        'change_form': change_form,
        'student': student,
    }
    return render(request, 'student-profile.html', context)



















#register
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib import messages

@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Account created successfully!'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                })
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f"{field}: {error}")
            
            return JsonResponse({
                'status': 'error',
                'message': errors[0]  # Return first error message
            })
    else:
        form = UserRegistrationForm()
    
    return render(request, 'admin-createAcc.html', {'form': form})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Class, Enrollment, GradingPeriod
from django.db.models import Count
import json
from decimal import Decimal
from .models import Class, Enrollment, SubjectCriterion, Activity, Score, GradingPeriod, SchoolYear

def get_top_students(teacher, section, grading_period=None, school_year=None, limit=5):
    # Filter classes based on the section and school year
    classes = Class.objects.filter(teacher=teacher, section=section, school_year=school_year)
    student_grades = []

    for class_obj in classes:
        enrollments = Enrollment.objects.filter(class_obj=class_obj).select_related('student')
        criteria = SubjectCriterion.objects.filter(subject=class_obj.subject).order_by('grading_criterion')

        for enrollment in enrollments:
            total_weighted_percentage = Decimal(0)

            for criterion in criteria:
                activities = Activity.objects.filter(
                    class_obj=class_obj,
                    subject_criterion=criterion,
                    grading_period=grading_period
                )
                
                if not activities.exists():
                    continue

                scores = Score.objects.filter(
                    enrollment=enrollment,
                    activity__in=activities
                )
                total_score = sum(score.score for score in scores)
                total_max_score = sum(activity.max_score for activity in activities)

                percentage = (Decimal(total_score) / Decimal(total_max_score) * Decimal(100)) if total_max_score > 0 else Decimal(0)
                weighted_percentage = percentage * (Decimal(criterion.weightage) / Decimal(100))
                total_weighted_percentage += weighted_percentage

            student_grades.append({
                'student': enrollment.student,
                'grade': total_weighted_percentage
            })

    return sorted(student_grades, key=lambda x: x['grade'], reverse=True)[:limit]


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Class, Enrollment, GradingPeriod, SchoolYear
import json

@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def teacher_dashboard(request):
    teacher = request.user.teacher
    current_school_year = SchoolYear.objects.filter(is_active=True).first()
    
    active_school_year = SchoolYear.objects.filter(is_active=True).first()

    # Filter classes based on the current school year
    classes = Class.objects.filter(teacher=teacher, school_year=current_school_year)
    class_data = (
        classes.values('section')
        .annotate(student_count=Count('enrollments__student', distinct=True))
        .order_by('section')
    )

    sections = [class_info['section'] for class_info in class_data]
    student_counts = [class_info['student_count'] for class_info in class_data]

    selected_section = request.GET.get('section', sections[0] if sections else None)
    
    grading_periods = GradingPeriod.objects.filter(school_year=active_school_year) if active_school_year else GradingPeriod.objects.none()
    first_grading = grading_periods.first()
    selected_grading_period_id = request.GET.get('grading_period', first_grading.id if first_grading else None)
    
    if selected_grading_period_id:
        selected_grading_period = GradingPeriod.objects.get(id=selected_grading_period_id)
    else:
        selected_grading_period = first_grading

    # Fetch the top 10 students for the selected section and grading period
    top_students = get_top_students(
        teacher,
        selected_section,
        selected_grading_period,
        current_school_year,
        limit=10  # Limit to top 10
    ) if selected_section else []

    # Get all enrollments for the teacher's classes
    all_enrollments = Enrollment.objects.filter(
        class_obj__teacher=teacher,
        class_obj__school_year=current_school_year
    ).select_related('student', 'class_obj')

    total_students = all_enrollments.values('student').distinct().count()
    passing_students = 0
    failing_students = 0

    for enrollment in all_enrollments:
        initial_grade = calculate_initial_grade(enrollment, selected_grading_period)
        if initial_grade >= 60:
            passing_students += 1
        else:
            failing_students += 1

    context = {
        'sections': json.dumps(sections),
        'student_counts': json.dumps(student_counts),
        'total_students': total_students,
        'section_choices': sections,
        'selected_section': selected_section,
        'grading_periods': grading_periods,
        'selected_grading_period': request.GET.get('grading_period', ''),
        'top_students': top_students,
        'passing_students': passing_students,
        'failing_students': failing_students,
        'current_school_year': current_school_year,
    }

    return render(request, 'teacher-dashboard.html', context)




def calculate_initial_grade(enrollment, grading_period):
    selected_class = enrollment.class_obj
    criteria = SubjectCriterion.objects.filter(subject=selected_class.subject).order_by('grading_criterion')
    
    total_weighted_percentage = Decimal(0)

    for criterion in criteria:
        activities = Activity.objects.filter(
            class_obj=selected_class,
            subject_criterion=criterion,
            grading_period=grading_period
        )
        
        if not activities.exists():
            continue

        scores = Score.objects.filter(
            enrollment=enrollment,
            activity__in=activities
        )
        total_score = sum(score.score for score in scores)
        total_max_score = sum(activity.max_score for activity in activities)

        percentage = (Decimal(total_score) / Decimal(total_max_score) * Decimal(100)) if total_max_score > 0 else Decimal(0)
        weighted_percentage = percentage * (Decimal(criterion.weightage) / Decimal(100))
        total_weighted_percentage += weighted_percentage

    return total_weighted_percentage


# You'll need to implement this function based on your existing code









# # views.py
# import json
# from django.shortcuts import render
# from django.http import JsonResponse
# from .models import Enrollment, Grade, Activity, Score
# import json
# from decimal import Decimal

# def decimal_default(obj):
#     if isinstance(obj, Decimal):
#         return float(obj)  # Convert Decimal to float
#     raise TypeError("Type not serializable")

# @login_required(login_url='login')
# @allowed_users(allowed_roles=['student'])
# def student_dashboard(request):
#     student = request.user.student
#     current_enrollments = Enrollment.objects.filter(
#         student=student,
#         class_obj__school_year__is_active=True
#     ).select_related('class_obj', 'class_obj__subject', 'class_obj__school_year')

#     # Get the active school year
#     active_school_year = current_enrollments.first().class_obj.school_year if current_enrollments else None

#     # Fetch notifications for each subject (teacher's uploaded grade)
#     grade_notifications = []
#     for enrollment in current_enrollments:
#         subject = enrollment.class_obj.subject
#         teacher = enrollment.class_obj.teacher
#         grading_periods = Grade.objects.filter(
#             enrollment=enrollment,
#             grading_period__school_year=active_school_year
#         ).values('grading_period__period', 'grading_period__id')

#         for period in grading_periods:
#             grade_notifications.append({
#                 'teacher': f"{teacher.Firstname} {teacher.Lastname}",  # Use first and last name
#                 'subject': subject.name,
#                 'grading_period': period['grading_period__period'],
#             })
#     grade_notifications = grade_notifications[:10]

#     # Fetch the grades for each subject by grading period
#     grade_trends = {}
#     for enrollment in current_enrollments:
#         subject = enrollment.class_obj.subject
#         grades = Grade.objects.filter(
#             enrollment=enrollment,
#             grading_period__school_year=active_school_year
#         ).order_by('grading_period__period')

#         # Add grades for each grading period
#         for grade in grades:
#             if subject.name not in grade_trends:
#                 grade_trends[subject.name] = {'periods': []}
#             grade_trends[subject.name]['periods'].append({
#                 'period': grade.grading_period.period,
#                 'grade': grade.quarterly_grade
#             })

#     # Calculate activity completion
#     total_activities = Activity.objects.filter(
#         class_obj__in=current_enrollments.values('class_obj')
#     ).count()
    
#     completed_activities = Score.objects.filter(
#         enrollment__in=current_enrollments,
#         score__gt=0
#     ).count()

#     completion_rate = (completed_activities / total_activities * 100) if total_activities > 0 else 0
#     context = {
#         'student': student,
#         'grade_trends': json.dumps(grade_trends, default=decimal_default),  # Use custom serializer
#         'grade_notifications': grade_notifications,
#         'completion_rate': round(completion_rate, 1),
#         'total_activities': total_activities,
#         'completed_activities': completed_activities,
#         'active_school_year': active_school_year,
#     }
    
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         return JsonResponse(context)
#     return render(request, 'student-dashboard.html', context)

import json
from django.db.models import Max
from django.shortcuts import render
from django.http import JsonResponse
from .models import Enrollment, Grade, Activity, Score, Subject
from decimal import Decimal

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)  # Convert Decimal to float
    raise TypeError("Type not serializable")

@login_required(login_url='login')
@allowed_users(allowed_roles=['student'])
def student_dashboard(request):
    student = request.user.student
    current_enrollments = Enrollment.objects.filter(
        student=student,
        class_obj__school_year__is_active=True
    ).select_related('class_obj', 'class_obj__subject', 'class_obj__school_year')

    # Get the active school year
    active_school_year = current_enrollments.first().class_obj.school_year if current_enrollments else None

    # Fetch the grades for each subject by grading period
    grade_trends = {}
    for enrollment in current_enrollments:
        subject = enrollment.class_obj.subject
        grades = Grade.objects.filter(
            enrollment=enrollment,
            grading_period__school_year=active_school_year
        ).order_by('grading_period__period')

        # Add grades for each grading period
        if subject.name not in grade_trends:
            grade_trends[subject.name] = {'periods': []}
        for grade in grades:
            grade_trends[subject.name]['periods'].append({
                'period': grade.grading_period.period,
                'grade': grade.quarterly_grade
            })

    # Calculate activity completion for each subject
    subject_activities = {}
    for subject in Subject.objects.all():
        total_activities = Activity.objects.filter(
            class_obj__in=current_enrollments.filter(class_obj__subject=subject).values('class_obj')
        ).count()
        completed_activities = Score.objects.filter(
            enrollment__in=current_enrollments.filter(class_obj__subject=subject),
            score__gt=0
        ).count()
        completion_rate = (completed_activities / total_activities * 100) if total_activities > 0 else 0
        subject_activities[subject.name] = {
            'total_activities': total_activities,
            'completed_activities': completed_activities,
            'completion_rate': round(completion_rate, 1)
        }

    # Calculate overall activity completion
    total_activities = sum(data['total_activities'] for data in subject_activities.values())
    completed_activities = sum(data['completed_activities'] for data in subject_activities.values())
    overall_completion_rate = (completed_activities / total_activities * 100) if total_activities > 0 else 0

    grade_notifications = []
    for enrollment in current_enrollments:
        subject = enrollment.class_obj.subject
        teacher = enrollment.class_obj.teacher
        grading_periods = Grade.objects.filter(
            enrollment=enrollment,
            grading_period__school_year=active_school_year
        ).values('grading_period__period', 'grading_period__id', 'created_at', 'updated_at')

        for period in grading_periods:
            grade_notifications.append({
                'teacher': f"{teacher.Firstname} {teacher.Lastname}",
                'subject': subject.name,
                'grading_period': period['grading_period__period'],
                'grading_period_id': period['grading_period__id'],
                'created_at': period['created_at'],  # Add the creation timestamp
                'updated_at': period['updated_at'],  # Add the update timestamp
            })

    # Sort the notifications by the 'updated_at' or 'created_at' to prioritize the latest updates
    grade_notifications = sorted(grade_notifications, key=lambda x: x['updated_at'], reverse=True)

    # Slice to get the latest 10 notifications
    grade_notifications = grade_notifications[:10]



    context = {
        'student': student,
        'grade_trends': json.dumps(grade_trends, default=decimal_default),  # Use custom serializer
        'grade_notifications': grade_notifications,
        'subject_activities': subject_activities,
        'overall_completion_rate': round(overall_completion_rate, 1),
        'total_activities': total_activities,
        'completed_activities': completed_activities,
        'active_school_year': active_school_year,
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(context)
    return render(request, 'student-dashboard.html', context)








#teacher-list
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
import logging
from .decorators import allowed_users
from .models import Teacher, Administrator, Class, Student

logger = logging.getLogger(__name__)

@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
@require_http_methods(["GET", "POST"])
def teacher_list(request):
    if request.method == 'POST':
        if 'change_pass' in request.POST:
            edit_id = request.POST.get('edit_id')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password and confirm_password:
                if new_password != confirm_password:
                    messages.error(request, "Passwords do not match.")
                    return redirect('teacher-list')

                user = get_object_or_404(User, id=edit_id)
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password updated successfully.")
            else:
                messages.error(request, "Please fill in both password fields.")
                return redirect('teacher-list')

        elif 'toggle_status' in request.POST:
            toggle_status_id = request.POST.get('toggle_status_id')
            current_status = request.POST.get('current_status')

            user = get_object_or_404(User, id=toggle_status_id)
            if current_status == 'active':
                user.is_active = False
                messages.success(request, f"Account for {user.email} has been deactivated successfully.")
            else:
                user.is_active = True
                messages.success(request, f"Account for {user.email} has been activated successfully.")
            user.save()
            return redirect('teacher-list')

        # Handle user update
        user_id = request.POST.get('user')
        print(f"User ID received: {user_id}")

        if not user_id:
            logger.error("User ID is empty")
            return JsonResponse({'status': 'error', 'message': 'User ID is required.'}, status=400)

        email = request.POST.get('email')
        firstname = request.POST.get('Firstname')
        lastname = request.POST.get('Lastname')
        middle_initial = request.POST.get('Middle-Initial')
        phone_number = request.POST.get('phone_number')
        gender = request.POST.get('gender')
        role = request.POST.get('role')
        status = request.POST.get('status')

        try:
            with transaction.atomic():
                user = User.objects.get(id=user_id)
                user.email = email
                user.is_active = (status == 'Active')

                # Store current role info for transition handling
                was_teacher = hasattr(user, 'teacher')

                # Handle role transition
                if role == 'Student' and was_teacher:
                    # Get teacher data before deletion
                    teacher_data = {
                        'Firstname': user.teacher.Firstname,
                        'Lastname': user.teacher.Lastname,
                        'Middle_Initial': user.teacher.Middle_Initial,
                        'Phone_Number': user.teacher.Phone_Number,
                        'Gender': user.teacher.Gender
                    }
                    
                    # Delete teacher profile
                    user.teacher.delete()
                    user.is_teacher = False
                    
                    # Create student profile with existing data
                    student = Student.objects.create(
                        user=user,
                        Firstname=teacher_data['Firstname'],
                        Lastname=teacher_data['Lastname'],
                        Middle_Initial=teacher_data['Middle_Initial'],
                        Phone_Number=teacher_data['Phone_Number'],
                        Gender=teacher_data['Gender']
                    )
                    user.is_student = True
                    messages.success(request, f"User role changed from Teacher to Student successfully.")

                elif role == 'Teacher':
                    # Update existing teacher profile or create new one
                    teacher, created = Teacher.objects.get_or_create(user=user)
                    teacher.Firstname = firstname
                    teacher.Lastname = lastname
                    teacher.Middle_Initial = middle_initial
                    teacher.Phone_Number = phone_number
                    teacher.Gender = gender
                    teacher.save()

                    user.is_teacher = True
                    # If user was a student, remove student profile
                    if hasattr(user, 'student'):
                        user.student.delete()
                        user.is_student = False
                        messages.success(request, f"User role changed from Student to Teacher successfully.")

                # Delete other role-specific objects if they exist
                Administrator.objects.filter(user=user).delete()

                user.save()
                logger.info(f"User {user_id} updated successfully with role {role}")
                return JsonResponse({
                    'status': 'success', 
                    'message': 'User updated successfully.',
                    'redirect': 'teacher-list' if role == 'Student' else None
                })

        except User.DoesNotExist:
            logger.error(f"User {user_id} not found")
            return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
        except Exception as e:
            logger.exception(f"Error updating user {user_id}: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while updating the user.'}, status=500)

    # Handle GET request for displaying the teacher list and searching
    sort_by = request.GET.get('sort', 'user__email')
    order = request.GET.get('order', 'asc')
    sort_order = sort_by if order == 'asc' else f'-{sort_by}'

    # Handle AJAX search requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.GET.get('query', '').strip()

        teachers = Teacher.objects.filter(
            Q(Firstname__icontains=query) | 
            Q(Lastname__icontains=query) |
            Q(user__email__icontains=query)
        ).select_related('user')

        return JsonResponse({
            'teachers': [
                {
                    'id': teacher.user.id,
                    'email': teacher.user.email,
                    'Firstname': teacher.Firstname,
                    'Lastname': teacher.Lastname,
                    'Middle_Initial': teacher.Middle_Initial,
                    'Phone_Number': teacher.Phone_Number,
                    'Gender': teacher.Gender,
                    'profile_picture': teacher.profile_picture.url if teacher.profile_picture else None,
                    'is_active': teacher.user.is_active
                }
                for teacher in teachers
            ]
        })

    teachers = Teacher.objects.select_related('user').order_by(sort_order)

    context = {
        'teachers': teachers,
        'sort_by': sort_by,
        'order': order,
    }

    return render(request, 'admin-TeacherList.html', context)


from django.http import JsonResponse
import json

@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
@require_http_methods(["POST"])
def delete_teacher(request):
    try:
        data = json.loads(request.body)  # Load JSON data from the request
        user_id = data.get('user_id')  # Get 'user_id' from parsed JSON data

        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'User ID is required.'}, status=400)

        with transaction.atomic():
            # Get user and related teacher object
            user = get_object_or_404(User, id=user_id)
            teacher = get_object_or_404(Teacher, user=user)

            # Delete teacher and user records
            teacher.delete()
            user.delete()

            logger.info(f"Teacher and user with ID {user_id} deleted successfully")
            return JsonResponse({'status': 'success', 'message': 'Teacher deleted successfully.'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        logger.exception(f"Error deleting user {user_id}: {str(e)}")
        return JsonResponse({'status': 'error', 'message': 'An error occurred while deleting the Teacher.'}, status=500)
    

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db import transaction
from .models import User, Teacher
import logging

logger = logging.getLogger(__name__)

@login_required(login_url='login')
@require_http_methods(["POST"])
def change_teacher_password(request):
    if not request.user.is_administrator:
        return JsonResponse({'status': 'error', 'message': 'Permission denied.'}, status=403)

    email = request.POST.get('email')
    new_password = request.POST.get('new_password')

    if not email or not new_password:
        logger.error("Email or new password is missing")
        return JsonResponse({'status': 'error', 'message': 'Email and new password are required.'}, status=400)

    try:
        with transaction.atomic():
            user = User.objects.get(email=email)
            if not hasattr(user, 'teacher'):
                logger.error(f"User with email {email} is not a teacher")
                return JsonResponse({'status': 'error', 'message': 'User is not a teacher.'}, status=400)

            user.set_password(new_password)
            user.save()

            logger.info(f"Password changed successfully for teacher: {email}")
            return JsonResponse({'status': 'success', 'message': 'Password changed successfully.'})

    except User.DoesNotExist:
        logger.error(f"User with email {email} not found")
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
    except Exception as e:
        logger.exception(f"Error changing password for teacher {email}: {str(e)}")
        return JsonResponse({'status': 'error', 'message': 'An error occurred while changing the password.'}, status=500)




from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
import logging
from django.db.models import Q
from .models import Student, User, Teacher, Administrator

logger = logging.getLogger(__name__)

@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
@require_http_methods(["GET", "POST"])
def student_list(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        print(f"User ID received: {user_id}")

        if not user_id:
            logger.error("User ID is empty")
            return JsonResponse({'status': 'error', 'message': 'User ID is required.'}, status=400)

        email = request.POST.get('email')
        firstname = request.POST.get('Firstname')
        lastname = request.POST.get('Lastname')
        middle_initial = request.POST.get('Middle-Initial')
        phone_number = request.POST.get('phone_number')
        gender = request.POST.get('gender')
        role = request.POST.get('role')
        status = request.POST.get('status')

        try:
            with transaction.atomic():
                user = User.objects.get(id=user_id)

                # Update User model fields
                user.email = email
                user.is_active = (status == 'Active')

                # Reset all roles first
                user.is_student = False
                user.is_teacher = False
                user.is_administrator = False

                # Create or update specific user types based on the selected role
                if role == 'Student':
                    user.is_student = True
                    student, created = Student.objects.get_or_create(user=user)
                    student.Firstname = firstname
                    student.Lastname = lastname
                    student.Middle_Initial = middle_initial
                    student.Phone_Number = phone_number
                    student.Gender = gender
                    student.save()

                    # Delete other role-specific objects if they exist
                    Teacher.objects.filter(user=user).delete()
                    Administrator.objects.filter(user=user).delete()
                elif role == 'Teacher':
                    user.is_teacher = True
                    teacher, created = Teacher.objects.get_or_create(user=user)
                    teacher.Firstname = firstname
                    teacher.Lastname = lastname
                    teacher.Middle_Initial = middle_initial
                    teacher.Phone_Number = phone_number
                    teacher.Gender = gender
                    teacher.save()

                    # Delete other role-specific objects if they exist
                    Student.objects.filter(user=user).delete()
                    Administrator.objects.filter(user=user).delete()
                elif role == 'Admin':
                    user.is_administrator = True
                    administrator, created = Administrator.objects.get_or_create(user=user)
                    administrator.Firstname = firstname
                    administrator.Lastname = lastname
                    administrator.Middle_Initial = middle_initial
                    administrator.Phone_Number = phone_number
                    administrator.Gender = gender
                    administrator.save()

                    # Delete other role-specific objects if they exist
                    Student.objects.filter(user=user).delete()
                    Teacher.objects.filter(user=user).delete()

                user.save()

                logger.info(f"User {user_id} updated successfully")
                return JsonResponse({'status': 'success', 'message': 'User updated successfully.'})

        except User.DoesNotExist:
            logger.error(f"User {user_id} not found")
            return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
        except Exception as e:
            logger.exception(f"Error updating user {user_id}: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while updating the user.'}, status=500)

    # Handle GET request for displaying the student list and searching
    sort_by = request.GET.get('sort', 'user__email')  # Default sort by email
    order = request.GET.get('order', 'asc')

    # Define the sorting field
    sort_order = sort_by if order == 'asc' else f'-{sort_by}'

    # Handle AJAX search requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.GET.get('query', '').strip()

        # Filter students based on the search query
        students = Student.objects.filter(
            Q(Firstname__icontains=query) | 
            Q(Lastname__icontains=query) |
            Q(user__email__icontains=query)
        ).select_related('user')

        # Prepare data for JSON response
        student_data = [
            {
                'user': {
                    'id': student.user.id,
                    'email': student.user.email,
                    'is_student': student.user.is_student,
                    'is_active': student.user.is_active,
                },
                'Firstname': student.Firstname,
                'Lastname': student.Lastname,
                'Middle_Initial': student.Middle_Initial,
                'Phone_Number': student.Phone_Number,
                'Gender': student.Gender,
                'profile_picture': student.profile_picture.url if student.profile_picture else None,
            }
            for student in students
        ]
        
        return JsonResponse({
            'students': [
                {
                    'id': student.user.id,
                    'email': student.user.email,
                    'Firstname': student.Firstname,
                    'Lastname': student.Lastname,
                    'Middle_Initial': student.Middle_Initial,
                    'Phone_Number': student.Phone_Number,
                    'Gender': student.Gender,
                    'profile_picture': student.profile_picture.url if student.profile_picture else None,
                    'is_active': student.user.is_active
                }
                for student in students
            ]
        })

    # Retrieve students with sorting for the initial page load
    students = Student.objects.select_related('user').order_by(sort_order)

    context = {
        'students': students,
        'sort_by': sort_by,
        'order': order,
    }

    return render(request, 'admin-StudentList.html', context)



from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db import transaction
from .models import User
import logging

logger = logging.getLogger(__name__)

@login_required(login_url='login')
@require_http_methods(["POST"])
def change_student_password(request):
    if not request.user.is_administrator:
        return JsonResponse({'status': 'error', 'message': 'Permission denied.'}, status=403)

    email = request.POST.get('email')
    new_password = request.POST.get('new_password')

    if not email or not new_password:
        logger.error("Email or new password is missing")
        return JsonResponse({'status': 'error', 'message': 'Email and new password are required.'}, status=400)

    try:
        with transaction.atomic():
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            logger.info(f"Password changed successfully for user: {email}")
            return JsonResponse({'status': 'success', 'message': 'Password changed successfully.'})

    except User.DoesNotExist:
        logger.error(f"User with email {email} not found")
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
    except Exception as e:
        logger.exception(f"Error changing password for user {email}: {str(e)}")
        return JsonResponse({'status': 'error', 'message': 'An error occurred while changing the password.'}, status=500)
    
    



from django.http import JsonResponse
import json

@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
@require_http_methods(["POST"])
def delete_student(request):
    try:
        data = json.loads(request.body)  # Load JSON data from the request
        user_id = data.get('user_id')  # Get 'user_id' from parsed JSON data

        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'User ID is required.'}, status=400)

        with transaction.atomic():
            # Get user and related student object
            user = get_object_or_404(User, id=user_id)
            student = get_object_or_404(Student, user=user)

            # Delete student and user records
            student.delete()
            user.delete()

            logger.info(f"Student and user with ID {user_id} deleted successfully")
            return JsonResponse({'status': 'success', 'message': 'Student deleted successfully.'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        logger.exception(f"Error deleting user {user_id}: {str(e)}")
        return JsonResponse({'status': 'error', 'message': 'An error occurred while deleting the student.'}, status=500)




@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
@require_http_methods(["GET"])
def administrator_list(request):
    # Get sort parameters from request
    sort_by = request.GET.get('sort', 'user__email')  # Default sort by email
    order = request.GET.get('order', 'asc')

    # Define the sorting field
    sort_order = sort_by if order == 'asc' else f'-{sort_by}'

    # Handle AJAX search requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.GET.get('query', '').strip()

        # Filter administrators based on the search query
        administrators = Administrator.objects.filter(
            Q(Firstname__icontains=query) | 
            Q(Lastname__icontains=query) |
            Q(user__email__icontains=query)
        ).select_related('user')

        # Prepare data for JSON response
        return JsonResponse({
            'administrators': [
                {
                    'id': admin.user.id,
                    'email': admin.user.email,
                    'Firstname': admin.Firstname,
                    'Lastname': admin.Lastname,
                    'Middle_Initial': admin.Middle_Initial,
                    'Phone_Number': admin.Phone_Number,
                    'Gender': admin.Gender,
                    'profile_picture': admin.profile_picture.url if admin.profile_picture else None,
                    'is_active': admin.user.is_active
                }
                for admin in administrators
            ]
        })

    # Retrieve administrators with sorting for the initial page load
    administrator = Administrator.objects.select_related('user').order_by(sort_order)

    context = {
        'administrator': administrator,
        'sort_by': sort_by,
        'order': order,
    }

    return render(request, 'admin-AdminList.html', context)




#subject Criteria
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Exists, OuterRef
from django.contrib import messages
from django.http import JsonResponse
from .models import Subject, SubjectCriterion, GradingCriterion
from .decorators import allowed_users

@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
def subject_criteria(request):
    if request.method == 'POST':
        if 'update_criteria' in request.POST:
            subject_id = request.POST.get('edit_subject_id')
            ww_weightage = request.POST.get('edit_ww_weightage')
            pt_weightage = request.POST.get('edit_pt_weightage')
            qe_weightage = request.POST.get('edit_qe_weightage')
            
            try:
                subject = Subject.objects.get(id=subject_id)
                
                criteria_types = ['WW', 'PT', 'QE']
                weightages = [ww_weightage, pt_weightage, qe_weightage]
                
                # Validate total weightage
                weightages = [int(w) if w else 0 for w in weightages]  # Default to 0 if empty
                total_weightage = sum(weightages)
                
                if total_weightage != 100:
                    raise ValueError("Total weightage must be exactly 100%")
                
                for criteria_type, weightage in zip(criteria_types, weightages):
                    SubjectCriterion.objects.update_or_create(
                        subject=subject,
                        grading_criterion=GradingCriterion.objects.get(criteria_type=criteria_type),
                        defaults={'weightage': weightage}
                    )
                
                messages.success(request, "Subject criteria updated successfully.")
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        elif 'subject_id' in request.POST:  # This checks if it's a new criteria submission
                subject_id = request.POST.get('subject_id')
                ww_weightage = request.POST.get('ww_weightage')
                pt_weightage = request.POST.get('pt_weightage')
                qe_weightage = request.POST.get('qe_weightage')
                
                try:
                    subject = Subject.objects.get(id=subject_id)
                    
                    criteria_types = ['WW', 'PT', 'QE']
                    weightages = [ww_weightage, pt_weightage, qe_weightage]
                    
                    total_weightage = sum(int(w) for w in weightages if w)
                    if total_weightage != 100:
                        raise ValueError("Total weightage must be exactly 100%")
                    
                    for criteria_type, weightage in zip(criteria_types, weightages):
                        SubjectCriterion.objects.create(
                            subject=subject,
                            grading_criterion=GradingCriterion.objects.get(criteria_type=criteria_type),
                            weightage=weightage
                        )
                    
                    messages.success(request, "Subject criteria added successfully.")
                except ValueError as e:
                    messages.error(request, str(e))
                except Exception as e:
                    messages.error(request, f"An error occurred: {str(e)}")

        elif 'clear_criteria' in request.POST:
            subject_id = request.POST.get('delete_id')
            try:
                subject = Subject.objects.get(id=subject_id)
                SubjectCriterion.objects.filter(subject=subject).delete()
                messages.success(request, f"Criteria for {subject.name} have been cleared.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        return redirect('subject-criteria')
    
    elif request.method == 'GET':
        if 'get_criteria' in request.GET:
            subject_id = request.GET.get('subject_id')
            try:
                subject = Subject.objects.get(id=subject_id)
                criteria = SubjectCriterion.objects.filter(subject=subject)
                
                data = {
                    'ww_weightage': criteria.get(grading_criterion__criteria_type='WW').weightage,
                    'pt_weightage': criteria.get(grading_criterion__criteria_type='PT').weightage,
                    'qe_weightage': criteria.get(grading_criterion__criteria_type='QE').weightage,
                }
                
                return JsonResponse(data)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
    
    subjects = Subject.objects.all()
    criteria = GradingCriterion.objects.all()
    subject_criteria = SubjectCriterion.objects.select_related('subject', 'grading_criterion').all()
    
    # Get subjects without criteria
    subjects_without_criteria = Subject.objects.annotate(
        has_criteria=Exists(SubjectCriterion.objects.filter(subject=OuterRef('pk')))
    ).filter(has_criteria=False)
    
    context = {
        'subjects': subjects,
        'criteria': criteria,
        'subject_criteria': subject_criteria,
        'subjects_without_criteria': subjects_without_criteria
    }
    
    return render(request, 'admin-SubjectCriteria.html', context)



#School Year
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .decorators import allowed_users
from .models import SchoolYear
from .forms import SchoolYearForm

@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
def manage_school_year(request):
    years = SchoolYear.objects.all().order_by('-year')
    
    if request.method == 'POST':
        if 'delete_id' in request.POST:
            # Handling delete action
            year_id = request.POST.get('delete_id')
            try:
                school_year = SchoolYear.objects.get(id=year_id)
                school_year.delete()
                return JsonResponse({'message': 'School Year deleted successfully.'}, status=200)
            except SchoolYear.DoesNotExist:
                return JsonResponse({'error': 'School Year not found.'}, status=404)
        
        year_id = request.POST.get('edit_id')
        form = SchoolYearForm(request.POST, instance=get_object_or_404(SchoolYear, id=year_id) if year_id else None)

        if form.is_valid():
            form.save()
            if year_id:
                return JsonResponse({'message': 'School Year updated successfully!'}, status=200)
            else:
                return JsonResponse({'message': 'School Year added successfully!'}, status=201)
        else:
            return JsonResponse({'error': 'Invalid form data make sure its unique.'}, status=400)
        
    form = SchoolYearForm()
    context = {
        'years': years,
        'form': form,
    }
    return render(request, 'admin-SchoolYear.html', context)




from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import render
from .models import Enrollment, Grade, GradingPeriod, SchoolYear, Subject, Student
import logging
from django.http import HttpResponse, FileResponse
import io
from django.templatetags.static import static
from django.contrib.sites.shortcuts import get_current_site
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
def admin_GradeReport(request):
    students = Student.objects.all()
    school_years = SchoolYear.objects.all().order_by('-year')
    logo_path = 'static/core/image/logo.png'
    logo_dep = 'core/static/core/image/logo-dep.png'

    if not school_years.exists():
        return render(request, 'admin-GradeReport.html', {'error': 'No school years found.'})

    subjects = Subject.objects.all()
    report_cards = []

    for student in students:
        for school_year in school_years:
            enrollments = Enrollment.objects.filter(student=student, class_obj__school_year=school_year)
            grading_periods = GradingPeriod.objects.filter(school_year=school_year).order_by('period')

            grades_data = {}
            subjects_with_final_grades = []  # Track subjects with valid final grades

            for subject in subjects:
                grades_data[subject.name] = {'quarterly_grades': {}}
                for period in grading_periods:
                    grade = Grade.objects.filter(
                        enrollment__student=student,
                        enrollment__class_obj__subject=subject,
                        grading_period=period
                    ).first()
                    grades_data[subject.name]['quarterly_grades'][period.period] = grade.quarterly_grade if grade else None

                # Calculate final grade only if there are quarterly grades
                quarterly_grades = [grade for grade in grades_data[subject.name]['quarterly_grades'].values() if grade is not None]
                if quarterly_grades:
                    final_grade = round(sum(quarterly_grades) / len(quarterly_grades), 2)
                    grades_data[subject.name]['final_grade'] = final_grade
                    grades_data[subject.name]['remarks'] = 'Passed' if final_grade >= 75 else 'Failed'
                    subjects_with_final_grades.append(final_grade)  # Add to list of valid final grades
                else:
                    grades_data[subject.name]['final_grade'] = None
                    grades_data[subject.name]['remarks'] = None

            # Calculate general average only for subjects with final grades
            general_average = round(sum(subjects_with_final_grades) / len(subjects_with_final_grades), 2) if subjects_with_final_grades else None

            grade_section = enrollments.first().class_obj.grade_level + ' - ' + enrollments.first().class_obj.section if enrollments.exists() else 'N/A'

            report_cards.append({
                'student': student,
                'school_year': school_year,
                'grades_data': grades_data,
                'grading_periods': grading_periods,
                'general_average': general_average,
                'grade_section': grade_section
            })

    # PDF export section remains the same
    if request.method == 'POST' and 'export' in request.POST:
        student_id = request.POST.get('student_id')
        school_year_id = request.POST.get('school_year_id')

        try:
            selected_student = Student.objects.get(user_id=student_id)
            selected_school_year = SchoolYear.objects.get(id=school_year_id)
            
            selected_enrollments = Enrollment.objects.filter(
                student=selected_student, 
                class_obj__school_year=selected_school_year
            )
            
            if not selected_enrollments.exists():
                return HttpResponse('No enrollment found for this student in the selected school year.')

            grading_periods = GradingPeriod.objects.filter(
                school_year=selected_school_year
            ).order_by('period')
            
            grades_data = {}
            subjects_with_final_grades = []  # Track subjects with valid final grades

            for enrollment in selected_enrollments:
                subject = enrollment.class_obj.subject
                grades_data[subject.name] = {'quarterly_grades': {}}
                
                for period in grading_periods:
                    grade = Grade.objects.filter(
                        enrollment=enrollment,
                        grading_period=period
                    ).first()
                    grades_data[subject.name]['quarterly_grades'][period.period] = grade.quarterly_grade if grade else None

                quarterly_grades = [grade for grade in grades_data[subject.name]['quarterly_grades'].values() if grade is not None]
                if quarterly_grades:
                    final_grade = round(sum(quarterly_grades) / len(quarterly_grades), 2)
                    grades_data[subject.name]['final_grade'] = final_grade
                    grades_data[subject.name]['remarks'] = 'Passed' if final_grade >= 75 else 'Failed'
                    subjects_with_final_grades.append(final_grade)  # Add to list of valid final grades
                else:
                    grades_data[subject.name]['final_grade'] = None
                    grades_data[subject.name]['remarks'] = None

            # Calculate general average only for subjects with final grades
            general_average = round(sum(subjects_with_final_grades) / len(subjects_with_final_grades), 2) if subjects_with_final_grades else None
            
            grade_section = f"{selected_enrollments.first().class_obj.grade_level} - {selected_enrollments.first().class_obj.section}"

            context = {
                'report_card': {
                    'student': selected_student,
                    'school_year': selected_school_year,
                    'grades_data': grades_data,
                    'grading_periods': grading_periods,
                    'general_average': general_average,
                    'grade_section': grade_section
                },
                'logo_path': logo_path,
                'logo_dep': logo_dep,
            }

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{selected_student.get_full_name()}_report_card.pdf"'

            template = get_template('ReportCard.html')
            html = template.render(context)

            pisa_status = pisa.CreatePDF(
                html,
                dest=response,
                encoding='UTF-8'
            )

            if pisa_status.err:
                return HttpResponse('Error generating PDF', status=500)
            
            return response

        except Exception as e:
            logger.exception("Error generating PDF")
            return HttpResponse(f'An error occurred while generating the PDF: {str(e)}', status=500)

    context = {
        'report_cards': report_cards,
        'logo_path': logo_path,
        'logo_dep': logo_dep,
    }

    return render(request, 'admin-GradeReport.html', context)





from django.http import JsonResponse
from django.shortcuts import render
from django.contrib import messages
from .models import SchoolYear, GradingPeriod
from django.views.decorators.csrf import csrf_exempt

@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
@csrf_exempt  # Use this only if you're making POST requests without CSRF tokens (e.g., via AJAX)
def admin_GradingPeriod(request):
    current_school_year = SchoolYear.objects.filter(is_active=True).first()
    grading_periods = GradingPeriod.objects.filter(school_year=current_school_year).order_by('period') if current_school_year else []

    if request.method == 'POST':
        if 'add_grading_period' in request.POST:
            period = request.POST.get('period')
            is_current = request.POST.get('is_current') == 'True'

            if current_school_year:
                # Check for duplicates
                existing_period = GradingPeriod.objects.filter(school_year=current_school_year, period=period).first()
                if existing_period:
                    return JsonResponse({'status': 'error', 'message': 'Grading Period already exists.'}, status=400)
                
                # Create new grading period
                GradingPeriod.objects.create(
                    school_year=current_school_year,
                    period=period,
                    is_current=is_current
                )
                return JsonResponse({'status': 'success', 'message': 'Grading Period added successfully.'})

            return JsonResponse({'status': 'error', 'message': 'No active school year found.'}, status=400)

        # Handling other POST actions like edit and delete
        elif 'edit_grading_period' in request.POST:
            grading_period_id = request.POST.get('edit_id')
            is_current = request.POST.get('is_current') == 'True'
            
            grading_period = GradingPeriod.objects.get(id=grading_period_id)
            grading_period.is_current = is_current
            grading_period.save()
            return JsonResponse({'status': 'success', 'message': 'Grading Period updated successfully.'})

        elif 'delete_grading_period' in request.POST:
            grading_period_id = request.POST.get('delete_id')
            GradingPeriod.objects.filter(id=grading_period_id).delete()
            return JsonResponse({'status': 'success', 'message': 'Grading Period deleted successfully.'})

    context = {
        'current_school_year': current_school_year,
        'grading_periods': grading_periods,
    }
    return render(request, 'admin-GradingPeriod.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Subject
from .forms import SubjectForm
from .decorators import allowed_users

@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
def admin_subject(request):
    subjects = Subject.objects.all()

    if request.method == 'POST':
        if 'add_subject' in request.POST:
            form = SubjectForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Subject added successfully!')
            else:
                messages.error(request, 'Failed to add subject. Please check the form.')
        elif 'edit_subject' in request.POST:
            subject_id = request.POST.get('edit_id')
            subject = get_object_or_404(Subject, id=subject_id)
            form = SubjectForm(request.POST, instance=subject)
            if form.is_valid():
                form.save()
                messages.success(request, 'Subject updated successfully!')
            else:
                messages.error(request, 'Failed to update subject. Please check the form.')
        elif 'delete_subject' in request.POST:
            subject_id = request.POST.get('delete_id')
            subject = get_object_or_404(Subject, id=subject_id)
            subject.delete()
            messages.success(request, 'Subject deleted successfully!')
        return redirect('admin-subject')

    context = {
        'subjects': subjects,
        'form': SubjectForm()
    }
    return render(request, 'admin-Subject.html', context)


# class
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Case, When
from .forms import AddClassForm
from .models import Class, SchoolYear, Subject, Teacher
from .models import GradingPeriod

@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
def admin_class(request):
    current_school_year = SchoolYear.objects.filter(is_active=True).first()

    grade_order = Case(
        When(grade_level='Grade 7', then=0),
        When(grade_level='Grade 8', then=1),
        When(grade_level='Grade 9', then=2),
        When(grade_level='Grade 10', then=3),
    )
    current_classes = Class.objects.filter(school_year=current_school_year).order_by(grade_order, 'section')
    active_school_years = SchoolYear.objects.filter(is_active=True)
    teachers = Teacher.objects.all()
    subjects = Subject.objects.all()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            form = AddClassForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Class added successfully.')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Error in {field}: {error}')
        elif action == 'edit':
            class_id = request.POST.get('class_id')
            class_instance = get_object_or_404(Class, id=class_id)
            form = AddClassForm(request.POST, instance=class_instance)
            if form.is_valid():
                form.save()
                messages.success(request, 'Class updated successfully.')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Error in {field}: {error}')
        elif action == 'delete':
            class_id = request.POST.get('class_id')
            class_instance = get_object_or_404(Class, id=class_id)
            class_instance.delete()
            messages.success(request, 'Class deleted successfully.')
        return redirect('admin-class')
    form = AddClassForm()
    context = {
        'form': form,
        'current_classes': current_classes,
        'current_school_year': current_school_year,
        'active_school_years': active_school_years,
        'teachers': teachers,
        'subjects': subjects,
    }
    return render(request, 'admin-Class.html', context)



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from itertools import groupby
from operator import attrgetter
from .decorators import allowed_users
from .models import SchoolYear, Class

@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
def admin_prevClass(request):
    try:
        current_school_year = SchoolYear.objects.get(is_active=True)
    except SchoolYear.DoesNotExist:
        current_school_year = None

    if current_school_year:
        previous_classes = Class.objects.filter(
            ~Q(school_year=current_school_year)
        ).select_related('school_year', 'teacher', 'subject').order_by('-school_year__year', 'grade_level', 'section')
    else:
        previous_classes = Class.objects.all().select_related('school_year', 'teacher', 'subject').order_by('-school_year__year', 'grade_level', 'section')

    # Group classes by school year
    grouped_classes = {}
    for school_year, classes in groupby(previous_classes, key=attrgetter('school_year.year')):
        grouped_classes[school_year] = sorted(classes, key=lambda c: ['Grade 7', 'Grade 8', 'Grade 9', 'Grade 10'].index(c.grade_level))

    context = {
        'grouped_classes': grouped_classes,
        'current_school_year': current_school_year,
    }
    return render(request, 'admin-prevClass.html', context)







#teacher-myclassAdvisory
@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def teacher_myClassAdvisory(request):
    teacher = request.user.teacher
    
    # Get the current school year
    current_school_year = SchoolYear.objects.filter(is_active=True).first()

    # Query all advisory classes for the teacher in the current school year
    current_advisories = Class.objects.filter(
        teacher=teacher,
        school_year=current_school_year
    ).select_related('subject', 'school_year').annotate(
        student_count=Count('enrollments')
    )

    # Query grading periods for the current school year only
    grading_periods = GradingPeriod.objects.filter(school_year=current_school_year)

    # Handle the class selection
    selected_class_id = request.GET.get('class')
    if selected_class_id:
        selected_class = get_object_or_404(Class, id=selected_class_id, teacher=teacher)
        request.session['selected_class_id'] = selected_class.id
        return redirect('teacher-myClassRecord')

    context = {
        'current_advisories': current_advisories,
        'grading_periods': grading_periods,
        'current_school_year': current_school_year,
    }
    return render(request, 'teacher-ClassAdvisory.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def teacher_SummaryGrades(request):
    teacher = request.user.teacher
    
    # Get the current school year
    current_school_year = SchoolYear.objects.filter(is_active=True).first()

    # Query all advisory classes for the teacher in the current school year
    current_advisories = Class.objects.filter(
        teacher=teacher,
        school_year=current_school_year
    ).select_related('subject', 'school_year').annotate(
        student_count=Count('enrollments')
    )

    # Query grading periods for the current school year only
    grading_periods = GradingPeriod.objects.filter(school_year=current_school_year)

    # Handle the class selection
    selected_class_id = request.GET.get('class')
    if selected_class_id:
        selected_class = get_object_or_404(Class, id=selected_class_id, teacher=teacher)
        request.session['selected_class_id'] = selected_class.id
        return redirect('teacher-QuarterSummary')

    context = {
        'current_advisories': current_advisories,
        'grading_periods': grading_periods,
        'current_school_year': current_school_year,
    }

    return render(request, 'teacher-SummaryGrade.html', context)


from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.shortcuts import get_object_or_404
from decimal import Decimal


logo_path = 'static/core/image/logo.png'
logo_dep = 'core/static/core/image/logo-dep.png'
@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def teacher_QuarterSummary(request):
    class_id = request.GET.get('class')
    selected_class = get_object_or_404(Class, id=class_id) if class_id else None
    
    if not selected_class:
        messages.error(request, "Please select a class.")
        return render(request, 'quarter_summary.html', {'selected_class': None})

    # Get all enrollments for the selected class
    enrollments = Enrollment.objects.filter(class_obj=selected_class).select_related('student')
    
    # Get all grading periods for the current school year
    grading_periods = GradingPeriod.objects.filter(
        school_year=selected_class.school_year
    ).order_by('period')

    # Create a list to store student grade data
    students_data = []

    for enrollment in enrollments:
        student_grades = {
            'student_name': enrollment.student.get_full_name(),
            'grades': {},
            'final_grade': Decimal('0.00'),
            'remarks': ''
        }

        # Get grades for each quarter
        total_grade = Decimal('0.00')
        grade_count = 0

        for period in grading_periods:
            try:
                grade = Grade.objects.get(
                    enrollment=enrollment,
                    grading_period=period
                )
                student_grades['grades'][period.period] = grade.quarterly_grade
                total_grade += grade.quarterly_grade
                grade_count += 1
            except Grade.DoesNotExist:
                student_grades['grades'][period.period] = None

        # Calculate final grade if there are any grades
        if grade_count > 0:
            student_grades['final_grade'] = (total_grade / grade_count).quantize(Decimal('0.01'))
            student_grades['remarks'] = 'PASSED' if student_grades['final_grade'] >= 75 else 'FAILED'

        students_data.append(student_grades)

    # If export is requested (PDF)
    if request.GET.get('export') == 'pdf':
        template = get_template('quarter_summary_pdf.html')
        context = {
            'selected_class': selected_class,
            'students_data': students_data,
            'grading_periods': grading_periods,
            'logo_path': logo_path,  
            'logo_dep': logo_dep,
            'school_year': selected_class.school_year,
        }
        html_content = template.render(context)

        # Generate PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="quarter_summary.pdf"'  # Change 'inline' to 'attachment'
        pisa_status = pisa.CreatePDF(html_content, dest=response)

        if pisa_status.err:
            return HttpResponse('Error generating PDF', status=500)
        return response

    # Render the normal page if not exporting
    context = {
        'selected_class': selected_class,
        'students_data': students_data,
        'grading_periods': grading_periods,
        'school_year': selected_class.school_year,
        
    }

    return render(request, 'teacher-QuarterSummary.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def teacher_prevSummaryGrade(request):
    previous_school_years = SchoolYear.objects.filter(is_active=False).order_by('-year')
    
    # Create a dictionary to store classes grouped by school year
    grouped_classes = {}
    
    for school_year in previous_school_years:
        # Get classes for current school year
        year_classes = Class.objects.filter(
            teacher=request.user.teacher,
            school_year=school_year
        ).select_related('school_year', 'subject').annotate(
            student_count=Count('enrollments')
        ).order_by('subject__name')
        
        # Add to dictionary only if classes exist
        if year_classes.exists():
            grouped_classes[school_year] = year_classes

    context = {
        'grouped_classes': grouped_classes,
    }

    return render(request, 'teacher-prevSummaryGrade.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Class, SchoolYear, GradingPeriod
from .decorators import allowed_users
from django.db.models import Count
import json

@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def teacher_prevClassAdvisory(request):
    teacher = request.user.teacher
    
    # Get the current school year
    current_school_year = SchoolYear.objects.filter(is_active=True).first()

    # Query all previous school years
    previous_school_years = SchoolYear.objects.filter(is_active=False).order_by('-year')

    # Query all previous classes for the teacher
    previous_classes = Class.objects.filter(
        teacher=teacher,
        school_year__is_active=False
    ).select_related('subject', 'school_year').annotate(
        student_count=Count('enrollments')
    ).order_by('-school_year__year', 'grade_level', 'section')

    # Group classes by school year
    classes_by_year = {}
    for class_obj in previous_classes:
        year = class_obj.school_year.year
        if year not in classes_by_year:
            classes_by_year[year] = []
        classes_by_year[year].append(class_obj)

    # Query grading periods for each school year
    grading_periods_by_year = {}
    for school_year in previous_school_years:
        grading_periods = GradingPeriod.objects.filter(school_year=school_year)
        grading_periods_by_year[school_year.year] = [
            {'id': period.id, 'period': f"{school_year.year} - {period.period}"}
            for period in grading_periods
        ]

    # Convert grading_periods_by_year to JSON for use in JavaScript
    grading_periods_json = json.dumps(grading_periods_by_year)


    # Handle the class selection
    selected_class_id = request.GET.get('class')
    if selected_class_id:
        selected_class = get_object_or_404(Class, id=selected_class_id, teacher=teacher)
        request.session['selected_class_id'] = selected_class.id
        return redirect('teacher-myClassRecord')

    context = {
        'classes_by_year': classes_by_year,
        'grading_periods_json': grading_periods_json,
        'current_school_year': current_school_year,
        'previous_school_years': previous_school_years,
    }
    return render(request, 'teacher-prevClassAdvisory.html', context)


#teacher-myclassRecord
# working code


# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.core.exceptions import ValidationError, ObjectDoesNotExist
# from django.contrib.auth.decorators import login_required
# from django.http import JsonResponse
# from .models import Class, Student, Enrollment, Score, Activity, SubjectCriterion, User, GradingPeriod
# from .decorators import allowed_users
# from django.db import transaction

# @login_required(login_url='login')
# @allowed_users(allowed_roles=['teacher'])
# def teacher_myClassRecord(request):
#     selected_class_id = request.session.get('selected_class_id')
#     selected_class = None
#     enrollments = []
#     subject_criteria = []
#     current_grading_periods = GradingPeriod.objects.filter(is_current=True)

#     if selected_class_id:
#         try:
#             selected_class = get_object_or_404(Class, id=selected_class_id, teacher=request.user.teacher)
#             enrollments = Enrollment.objects.filter(class_obj=selected_class).select_related('student')

#             # Fetch scores for each enrollment
#             for enrollment in enrollments:
#                 enrollment.scores = Score.objects.filter(enrollment=enrollment).select_related('activity')
#                 for score in enrollment.scores:
#                     score.enrollment_id = enrollment.id
#                     score.activity_id = score.activity.id

#             # Fetch subject criteria for the class subject
#             subject_criteria = SubjectCriterion.objects.filter(subject=selected_class.subject)

#             all_students = Student.objects.all().order_by('Lastname', 'Firstname')
#             enrolled_students = set(enrollment.student for enrollment in enrollments)

#             if request.method == 'POST':
#                 if 'student_email' in request.POST:
#                     student_email = request.POST.get('student_email')
#                     if student_email:
#                         try:
#                             user = User.objects.get(email=student_email, is_student=True)
#                             student = user.student
#                             if student not in enrolled_students:
#                                 enrollment = Enrollment(class_obj=selected_class, student=student)
#                                 enrollment.clean()  # Manually call the clean method to trigger validation
#                                 enrollment.save()
#                                 messages.success(request, f"{student} has been added to the class.")
#                             else:
#                                 messages.warning(request, f"{student} is already in this class.")
#                         except User.DoesNotExist:
#                             messages.error(request, f"No student found with email: {student_email}")
#                         except Student.DoesNotExist:
#                             messages.error(request, f"User with email {student_email} is not registered as a student.")
#                         except ValidationError as e:
#                             messages.error(request, e.message)

#                 elif 'add_activity' in request.POST:
#                     criterion_id = request.POST.get('subject_criterion')
#                     grading_period_id = request.POST.get('grading_period')
#                     activity_name = request.POST.get('activity_name')
#                     max_score = request.POST.get('max_score')

#                     if not all([criterion_id, grading_period_id, activity_name, max_score]):
#                         messages.error(request, "All fields are required to add an activity.")
#                     else:
#                         try:
#                             with transaction.atomic():
#                                 criterion = SubjectCriterion.objects.get(id=criterion_id)
#                                 grading_period = GradingPeriod.objects.get(id=grading_period_id)
                                
#                                 activity = Activity(
#                                     name=activity_name,
#                                     class_obj=selected_class,
#                                     subject_criterion=criterion,
#                                     grading_period=grading_period,
#                                     max_score=max_score
#                                 )
#                                 activity.full_clean()  # Validate the model
#                                 activity.save()
#                                 messages.success(request, f"Activity '{activity_name}' has been added successfully.")
#                         except SubjectCriterion.DoesNotExist:
#                             messages.error(request, "The selected subject criterion does not exist.")
#                         except GradingPeriod.DoesNotExist:
#                             messages.error(request, "The selected grading period does not exist.")
#                         except ValidationError as e:
#                             messages.error(request, f"Validation error: {', '.join(e.messages)}")
#                         except Exception as e:
#                             messages.error(request, f"An unexpected error occurred: {str(e)}")
                    
#                 elif 'add_score' in request.POST:
#                     enrollment_id = request.POST.get('enrollment')
#                     activity_id = request.POST.get('activity')
#                     score_value = request.POST.get('score')

#                     try:
#                         enrollment = Enrollment.objects.get(id=enrollment_id)
#                         activity = Activity.objects.get(id=activity_id)

#                         # Check if score is valid
#                         if float(score_value) > activity.max_score:
#                             raise ValidationError("Score cannot be higher than the max score for the activity.")

#                         score = Score(
#                             enrollment=enrollment,
#                             activity=activity,
#                             score=float(score_value)
#                         )
#                         score.full_clean()  # This will run the validation
#                         score.save()
#                         messages.success(request, 'Score added successfully.')
#                     except ValidationError as e:
#                         messages.error(request, f"Validation error: {e}")
#                     except Exception as e:
#                         messages.error(request, f"An error occurred: {e}")

#                 elif 'remove_id' in request.POST:
#                     enrollment_id = request.POST.get('remove_id')
#                     if enrollment:
#                         try:
#                             enrollment = Enrollment.objects.get(id=enrollment_id, class_obj=selected_class)
#                             student_name = f"{enrollment.student.Lastname} {enrollment.student.Firstname}"
#                             enrollment.delete()
#                             messages.success(request, f'{student_name} removed from class successfully.')
#                         except Enrollment.DoesNotExist:
#                             messages.error(request, 'The student enrollment record does not exist.')
#                         except Exception as e:
#                             messages.error(request, f"An error occurred: {str(e)}")
#                     else:
#                         messages.error(request, "No valid ID provided for student removal.")
#                 else:
#                     print("No remove_id found in POST data")

#         except ObjectDoesNotExist as e:
#             messages.error(request, f"Error: {str(e)}")
#         except AttributeError as e:
#             messages.error(request, f"Error: {str(e)}")

#     else:
#         messages.info(request, "No class selected or empty.")

    
#     enrollments = Enrollment.objects.filter(class_obj=selected_class)

#     context = {
#         'selected_class': selected_class,
#         'enrollments': enrollments,
#         'subject_criteria': subject_criteria,
#         'grading_periods': current_grading_periods,
#         'activities': Activity.objects.filter(class_obj=selected_class) if selected_class else [],
#         'students': Student.objects.filter(enrollments__class_obj=selected_class) if selected_class else []
#     }

#     return render(request, 'teacher-ClassRecord.html', context)



#get_different score
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Class, Enrollment, Score, Activity, GradingPeriod

def get_scores(request):
    selected_class_id = request.GET.get('class_id')
    selected_criteria = request.GET.get('criteria')
    selected_grading_period = request.GET.get('grading_period')
    
    selected_class = get_object_or_404(Class, id=selected_class_id)
    grading_period = get_object_or_404(GradingPeriod, period=selected_grading_period, school_year=selected_class.school_year)
    
    activities = Activity.objects.filter(
        class_obj=selected_class,
        subject_criterion__grading_criterion__criteria_type=selected_criteria,
        grading_period=grading_period
    ).order_by('date_created')
    
    enrollments = Enrollment.objects.filter(class_obj=selected_class)
    
    scores_data = []
    for enrollment in enrollments:
        student_scores = []
        for activity in activities:
            score = Score.objects.filter(enrollment=enrollment, activity=activity).first()
            if score:
                student_scores.append({
                    'activity_name': activity.name,
                    'date_created': activity.date_created.strftime('%Y-%m-%d'),
                    'score': score.score,
                    'max_score': activity.max_score,
                    'enrollment_id': enrollment.id,
                    'activity_id': activity.id,
                })
        
        scores_data.append({
            'student': {
                'Firstname': enrollment.student.Firstname,
                'Lastname': enrollment.student.Lastname,
            },
            'scores': student_scores,
            'enrollment_id': enrollment.id,  # Always include the enrollment ID
        })
    
    return JsonResponse({
        'selected_class': selected_class.id,
        'selected_criteria': selected_criteria,
        'selected_grading_period': selected_grading_period,
        'scores_data': scores_data,
    })



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Class, Student, Enrollment, Score, Activity, SubjectCriterion, User, GradingPeriod
from .decorators import allowed_users
from django.db import transaction
import json

@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def teacher_myClassRecord(request):
    selected_class_id = request.session.get('selected_class_id')
    selected_class = None
    enrollments = []
    subject_criteria = []
    current_grading_periods = []

    if selected_class_id:
        try:
            selected_class = get_object_or_404(Class, id=selected_class_id, teacher=request.user.teacher)
            enrollments = Enrollment.objects.filter(class_obj=selected_class).select_related('student')

            # Fetch scores for each enrollment
            for enrollment in enrollments:
                enrollment.scores = Score.objects.filter(enrollment=enrollment).select_related('activity')
                # If scores are hidden and user is not the teacher, mask the scores
                if selected_class.hide_scores and not request.user.teacher == selected_class.teacher:
                    for score in enrollment.scores:
                        score.score = "Hidden"
                else:
                    for score in enrollment.scores:
                        score.enrollment_id = enrollment.id
                        score.activity_id = score.activity.id

            # Fetch subject criteria for the class subject
            subject_criteria = SubjectCriterion.objects.filter(subject=selected_class.subject)


            current_grading_periods = GradingPeriod.objects.filter(school_year=selected_class.school_year)

            all_students = Student.objects.all().order_by('Lastname', 'Firstname')
            enrolled_students = set(enrollment.student for enrollment in enrollments)

            if request.method == 'POST':
                if 'student_email' in request.POST:
                    student_email = request.POST.get('student_email')
                    if student_email:
                        try:
                            user = User.objects.get(email=student_email, is_student=True)
                            student = user.student
                            if student not in enrolled_students:
                                enrollment = Enrollment(class_obj=selected_class, student=student)
                                enrollment.clean()  # Manually call the clean method to trigger validation
                                enrollment.save()
                                messages.success(request, f"{student} has been added to the class.")
                            else:
                                messages.warning(request, f"{student} is already in this class.")
                        except User.DoesNotExist:
                            messages.error(request, f"No student found with email: {student_email}")
                        except Student.DoesNotExist:
                            messages.error(request, f"User with email {student_email} is not registered as a student.")
                        except ValidationError as e:
                            messages.error(request, e.message)

                elif 'add_activity' in request.POST:
                    criterion_id = request.POST.get('subject_criterion')
                    grading_period_id = request.POST.get('grading_period')
                    activity_name = request.POST.get('activity_name')
                    max_score = request.POST.get('max_score')

                    if not all([criterion_id, grading_period_id, activity_name, max_score]):
                        messages.error(request, "All fields are required to add an activity.")
                    else:
                        try:
                            with transaction.atomic():
                                criterion = SubjectCriterion.objects.get(id=criterion_id)
                                grading_period = GradingPeriod.objects.get(id=grading_period_id)
                                
                                activity = Activity(
                                    name=activity_name,
                                    class_obj=selected_class,
                                    subject_criterion=criterion,
                                    grading_period=grading_period,
                                    max_score=max_score
                                )
                                activity.full_clean()  # Validate the model
                                activity.save()
                                messages.success(request, f"Activity '{activity_name}' has been added successfully.")
                        except SubjectCriterion.DoesNotExist:
                            messages.error(request, "The selected subject criterion does not exist.")
                        except GradingPeriod.DoesNotExist:
                            messages.error(request, "The selected grading period does not exist.")
                        except ValidationError as e:
                            messages.error(request, f"Validation error: {', '.join(e.messages)}")
                        except Exception as e:
                            messages.error(request, f"An unexpected error occurred: {str(e)}")
                    
                elif 'add_score' in request.POST:
                    enrollment_id = request.POST.get('enrollment')
                    activity_id = request.POST.get('activity')
                    score_value = request.POST.get('score')

                    try:
                        enrollment = Enrollment.objects.get(id=enrollment_id)
                        activity = Activity.objects.get(id=activity_id)

                        # Check if score is valid
                        if float(score_value) > activity.max_score:
                            raise ValidationError("Score cannot be higher than the max score for the activity.")

                        score = Score(
                            enrollment=enrollment,
                            activity=activity,
                            score=float(score_value)
                        )
                        score.full_clean()  # This will run the validation
                        score.save()
                        messages.success(request, 'Score added successfully.')

                        # Pass enrollment data to template context for rendering
                        enrollments = Enrollment.objects.filter(class_obj=selected_class).select_related('student')
                        context = {
                            'selected_class': selected_class,
                            'enrollments': enrollments,
                            'subject_criteria': subject_criteria,
                            'grading_periods': current_grading_periods,
                            'activities': Activity.objects.filter(class_obj=selected_class),
                            'students': Student.objects.filter(enrollments__class_obj=selected_class),
                            'enrollment_id': enrollment.id,  # Pass enrollment ID to template
                        }
                        return render(request, 'teacher-ClassRecord.html', context)

                    except ValidationError as e:
                        messages.error(request, f"Validation error: {e}")
                    except Exception as e:
                        messages.error(request, f"An error occurred: {e}")


                if 'remove_id' in request.POST:
                    enrollment_id = request.POST.get('remove_id')
                    if enrollment_id:
                        try:
                            enrollment = Enrollment.objects.get(id=enrollment_id, class_obj=selected_class)
                            student_name = f"{enrollment.student.Lastname} {enrollment.student.Firstname}"
                            enrollment.delete()
                            return JsonResponse({
                                'success': True,
                                'message': f'{student_name} removed from class successfully.'
                            })
                        except Enrollment.DoesNotExist:
                            return JsonResponse({
                                'success': False,
                                'error': 'The student enrollment record does not exist.'
                            })
                        except Exception as e:
                            return JsonResponse({
                                'success': False,
                                'error': f"An error occurred: {str(e)}"
                            })
                    else:
                        return JsonResponse({
                            'success': False,
                            'error': "No valid ID provided for student removal."
                        })
        except ObjectDoesNotExist as e:
            messages.error(request, f"Error: {str(e)}")
        except AttributeError as e:
            messages.error(request, f"Error: {str(e)}")

    else:
        messages.info(request, "No class selected or empty.")

    
    enrollments = Enrollment.objects.filter(class_obj=selected_class)

    context = {
        'selected_class': selected_class,
        'enrollments': enrollments,
        'subject_criteria': subject_criteria,
        'grading_periods': current_grading_periods,
        'activities': Activity.objects.filter(class_obj=selected_class) if selected_class else [],
        'students': Student.objects.filter(enrollments__class_obj=selected_class) if selected_class else [],
        'hide_scores': selected_class.hide_scores if selected_class else False
    }

    return render(request, 'teacher-ClassRecord.html', context)


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Enrollment, Score
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def remove_student(request):
    try:
        data = json.loads(request.body)
        enrollment_id = data.get('enrollment_id')
        
        logger.info(f'Received request to remove student. Enrollment ID: {enrollment_id}')
        
        if not enrollment_id:
            logger.error(f'Invalid enrollment_id in request: {enrollment_id}')
            return JsonResponse({'success': False, 'error': 'Invalid or missing enrollment_id'}, status=400)
        
        try:
            enrollment_id = int(enrollment_id)
        except ValueError:
            logger.error(f'enrollment_id is not a valid integer: {enrollment_id}')
            return JsonResponse({'success': False, 'error': 'enrollment_id must be a valid integer'}, status=400)
        
        with transaction.atomic():
            enrollment = get_object_or_404(Enrollment, id=enrollment_id)
            student_name = f"{enrollment.student.Firstname} {enrollment.student.Lastname}"
            
            logger.info(f'Removing student: {student_name} (Enrollment ID: {enrollment_id})')
            
            # Delete associated scores (if any)
            Score.objects.filter(enrollment=enrollment).delete()
            
            # Now delete the enrollment
            enrollment.delete()
            
            logger.info(f'Successfully removed student: {student_name}')
        
        return JsonResponse({
            'success': True,
            'message': f'{student_name} has been removed from the class.'
        })
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON in request body: {str(e)}')
        return JsonResponse({'success': False, 'error': 'Invalid JSON in request body'}, status=400)
    except Enrollment.DoesNotExist:
        logger.error(f'Enrollment not found: {enrollment_id}')
        return JsonResponse({'success': False, 'error': 'Enrollment not found'}, status=404)
    except Exception as e:
        logger.exception(f"Unexpected error in remove_student view: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

 




# views.py
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .models import Score, Enrollment, Activity
from decimal import Decimal

@require_POST
@transaction.atomic
@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def update_score(request):
    enrollment_id = request.POST.get('enrollment_id')
    activity_id = request.POST.get('activity_id')
    new_score = request.POST.get('score')

    print(f"Received data: enrollment_id={enrollment_id}, activity_id={activity_id}, new_score={new_score}")

    if not all([enrollment_id, activity_id, new_score]):
        return JsonResponse({'success': False, 'error': 'Missing required parameters.'}, status=400)

    try:
        enrollment = Enrollment.objects.get(id=enrollment_id)
        activity = Activity.objects.get(id=activity_id)
        
        # Get or create the Score object
        score, created = Score.objects.get_or_create(
            enrollment=enrollment,
            activity=activity,
            defaults={'score': Decimal(new_score)}
        )
        
        if not created:
            score.score = Decimal(new_score)
        
        # Validate the score
        if score.score > activity.max_score:
            return JsonResponse({'success': False, 'error': f'Score cannot exceed maximum of {activity.max_score}'}, status=400)
        
        score.full_clean()  # This will run the model's validation
        score.save()
        
        return JsonResponse({'success': True, 'message': 'Score updated successfully'})
    
    except Enrollment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Enrollment not found.'}, status=404)
    
    except Activity.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Activity not found.'}, status=404)
    
    except ValidationError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid score value.'}, status=400)
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return JsonResponse({'success': False, 'error': 'An unexpected error occurred.'}, status=500)








#edit-Activity
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from .models import Class, Activity, SubjectCriterion

@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def edit_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)

    if request.method == 'POST':
        subject_criterion_id = request.POST.get('subject_criterion')
        activity_name = request.POST.get('activity_name')
        max_score = request.POST.get('max_score')

        if subject_criterion_id:
            subject_criterion = get_object_or_404(SubjectCriterion, id=subject_criterion_id)
            activity.subject_criterion = subject_criterion

        if activity_name:
            activity.name = activity_name

        if max_score:
            try:
                activity.max_score = float(max_score)
            except ValueError:
                messages.error(request, 'Invalid max score value.')

        try:
            activity.full_clean()  # This will run the validation
            activity.save()
            messages.success(request, 'Activity updated successfully.')
        except ValidationError as e:
            messages.error(request, f"Validation error: {', '.join(e.messages)}")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    return redirect('teacher-myClassRecord')




from django.http import JsonResponse
from .models import Activity

@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def get_activity_details(request, activity_id):
    try:
        activity = Activity.objects.get(id=activity_id)
        data = {
            'id': activity.id,
            'name': activity.name,
            'subject_criterion_id': activity.subject_criterion.id,
            'max_score': activity.max_score
        }
        return JsonResponse(data)
    except Activity.DoesNotExist:
        return JsonResponse({'error': 'Activity not found'}, status=404)
    

# Delete Activity
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Activity

@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def delete_activity(request):
    activity_id = request.POST.get('delete_id')
    if activity_id:
        try:
            activity = Activity.objects.get(id=activity_id)
            activity.delete()
            messages.success(request, f'Activity "{activity.name}" has been deleted successfully.')
        except Activity.DoesNotExist:
            messages.error(request, 'Activity not found.')
    else:
        messages.error(request, 'No activity selected for deletion.')
    
    return redirect('teacher-myClassRecord')  # Adjust this to your actual URL name



# views.py



# # views.py

# from decimal import Decimal
# from django.shortcuts import render, get_object_or_404
# from .models import Class, Enrollment, SubjectCriterion, Score, Student, Activity

# def teacher_gradeCalculate(request):
#     class_id = request.GET.get('class')
#     selected_class = get_object_or_404(Class, id=class_id)

#     # Get enrollments for this class
#     enrollments = Enrollment.objects.filter(class_obj=selected_class).select_related('student')

#     # Get criteria for this class's subject
#     criteria = SubjectCriterion.objects.filter(subject=selected_class.subject).order_by('grading_criterion')

#     results = []
#     for enrollment in enrollments:
#         student_result = {
#             'student': enrollment.student,
#             'criteria_scores': []
#         }

#         for criterion in criteria:
#             scores = Score.objects.filter(enrollment=enrollment, activity__subject_criterion=criterion)
#             total_score = sum(score.score for score in scores)
#             total_max_score = sum(score.activity.max_score for score in scores)

#             percentage = (Decimal(total_score) / Decimal(total_max_score) * Decimal(100)) if total_max_score > 0 else Decimal(0)

#             # Convert the percentage by the weight of the criteria
#             weighted_percentage = percentage * (Decimal(criterion.weightage) / Decimal(100))

#             #total the weigtage_percentage and become initial_grade
#             student_result['criteria_scores'].append({
#                 'criterion': criterion,
#                 'total_score': total_score,
#                 'total_max_score': total_max_score,
#                 'percentage': weighted_percentage,  # Store the weighted percentage
#             })

#         results.append(student_result)

#     # Calculate total max score for each criterion
#     total_max_scores = {
#         criterion.id: Activity.objects.filter(
#             subject_criterion=criterion
#         ).aggregate(
#             total_max_score=Sum('max_score')
#         )['total_max_score'] or Decimal(0)
#         for criterion in criteria
#     }

#     context = {
#         'selected_class': selected_class,
#         'results': results,
#         'criteria': criteria,
#         'total_max_scores': total_max_scores
#     }

#     return render(request, 'teacher-CalculateGrade.html', context)


from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from .models import Class, Enrollment, SubjectCriterion, Score, Student, Activity


def transmute_grade(initial_grade):
    transmutation_table = [
        (Decimal('98.40'), Decimal('99.99'), 99),
        (Decimal('96.80'), Decimal('98.39'), 98),
        (Decimal('95.20'), Decimal('96.79'), 97),
        (Decimal('93.60'), Decimal('95.19'), 96),
        (Decimal('92.00'), Decimal('93.59'), 95),
        (Decimal('90.40'), Decimal('91.99'), 94),
        (Decimal('88.80'), Decimal('90.39'), 93),
        (Decimal('87.20'), Decimal('88.79'), 92),
        (Decimal('85.60'), Decimal('87.19'), 91),
        (Decimal('84.00'), Decimal('85.59'), 90),
        (Decimal('82.40'), Decimal('83.99'), 89),
        (Decimal('80.80'), Decimal('82.39'), 88),
        (Decimal('79.20'), Decimal('80.79'), 87),
        (Decimal('77.60'), Decimal('79.19'), 86),
        (Decimal('76.00'), Decimal('77.59'), 85),
        (Decimal('74.40'), Decimal('75.99'), 84),
        (Decimal('72.80'), Decimal('74.39'), 83),
        (Decimal('71.20'), Decimal('72.79'), 82),
        (Decimal('69.60'), Decimal('71.19'), 81),
        (Decimal('68.00'), Decimal('69.59'), 80),
        (Decimal('66.40'), Decimal('67.99'), 79),
        (Decimal('64.80'), Decimal('66.39'), 78),
        (Decimal('63.20'), Decimal('64.79'), 77),
        (Decimal('61.60'), Decimal('63.19'), 76),
        (Decimal('60.00'), Decimal('61.59'), 75),
        (Decimal('56.00'), Decimal('59.99'), 74),
        (Decimal('52.00'), Decimal('55.99'), 73),
        (Decimal('48.00'), Decimal('51.99'), 72),
        (Decimal('44.00'), Decimal('47.99'), 71),
        (Decimal('40.00'), Decimal('43.99'), 70),
        (Decimal('36.00'), Decimal('39.99'), 69),
        (Decimal('32.00'), Decimal('35.99'), 68),
        (Decimal('28.00'), Decimal('31.99'), 67),
        (Decimal('24.00'), Decimal('27.99'), 66),
        (Decimal('20.00'), Decimal('23.99'), 65),
        (Decimal('16.00'), Decimal('19.99'), 64),
        (Decimal('12.00'), Decimal('15.99'), 63),
        (Decimal('8.00'), Decimal('11.99'), 62),
        (Decimal('4.00'), Decimal('7.99'), 61),
        (Decimal('0'), Decimal('3.99'), 60),
    ]
    
    for low, high, transmuted in transmutation_table:
        if low <= initial_grade <= high:
            return transmuted
    
    return 100 if initial_grade == 100 else 60  # Default to 60 for any grade below 4.00





from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.contrib.auth.decorators import login_required
from .decorators import allowed_users
from .models import Class, Enrollment, SubjectCriterion, Score, Student, Activity, GradingPeriod, SchoolYear

logo_path = 'static/core/image/logo.png'
logo_dep = 'core/static/core/image/logo-dep.png'

@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def teacher_gradeCalculate(request):
    class_id = request.GET.get('class')
    grading_period_id = request.GET.get('grading_period')
    selected_class = get_object_or_404(Class, id=class_id)
    grading_period = get_object_or_404(GradingPeriod, id=grading_period_id) if grading_period_id else None

    enrollments = Enrollment.objects.filter(class_obj=selected_class).select_related('student')
    criteria = SubjectCriterion.objects.filter(subject=selected_class.subject).order_by('grading_criterion')

    current_school_year = SchoolYear.objects.filter(is_active=True).first()
    is_current_school_year = selected_class.school_year == current_school_year

    results = []

    for enrollment in enrollments:
        student_result = {
            'student': enrollment.student,
            'criteria_scores': []
        }

        total_weighted_percentage = Decimal(0)

        for criterion in criteria:
            activities = Activity.objects.filter(
                class_obj=selected_class,
                subject_criterion=criterion,
                grading_period=grading_period
            )
            
            if not activities.exists():
                student_result['criteria_scores'].append({
                    'criterion': criterion,
                    'total_score': Decimal(0),
                    'total_max_score': Decimal(0),
                    'percentage': Decimal(0),
                })
                continue

            scores = Score.objects.filter(
                enrollment=enrollment,
                activity__in=activities
            )
            total_score = sum(score.score for score in scores)
            total_max_score = sum(activity.max_score for activity in activities)

            percentage = (Decimal(total_score) / Decimal(total_max_score) * Decimal(100)) if total_max_score > 0 else Decimal(0)
            weighted_percentage = percentage * (Decimal(criterion.weightage) / Decimal(100))
            total_weighted_percentage += weighted_percentage

            student_result['criteria_scores'].append({
                'criterion': criterion,
                'total_score': total_score,
                'total_max_score': total_max_score,
                'percentage': weighted_percentage,
            })

        student_result['initial_grade'] = total_weighted_percentage
        student_result['transmuted_grade'] = transmute_grade(total_weighted_percentage)
        student_result['quarterly_grade'] = student_result['transmuted_grade']

        results.append(student_result)

    # Sort results by quarterly_grade in descending order to rank correctly
    sorted_results = sorted(results, key=lambda x: x['quarterly_grade'], reverse=True)

    # Assign ranks with consideration for ties
    rank = 1
    for i, result in enumerate(sorted_results):
        if i > 0 and result['quarterly_grade'] == sorted_results[i - 1]['quarterly_grade']:
            result['rank'] = sorted_results[i - 1]['rank']  # Same rank as the previous student
        else:
            result['rank'] = rank  # Assign the current rank
        rank += 1  # Increment rank for the next student

    # Reorder the results back to the original order if needed (optional)
    # results = sorted(results, key=lambda x: x['student'].id)

    total_max_scores = {
        criterion.id: Activity.objects.filter(
            class_obj=selected_class,
            subject_criterion=criterion,
            grading_period=grading_period
        ).aggregate(
            total_max_score=Sum('max_score')
        )['total_max_score'] or Decimal(0)
        for criterion in criteria
    }

    context = {
        'selected_class': selected_class,
        'results': sorted_results,  # Use sorted_results to show ranks correctly
        'criteria': criteria,
        'total_max_scores': total_max_scores,
        'grading_period': grading_period,
        'is_current_school_year': is_current_school_year,
        'logo_path': logo_path,  
        'logo_dep': logo_dep,
    }

    if request.GET.get('export') == 'pdf':
        template = get_template('pdf_template.html')
        html = template.render(context)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{selected_class.grade_level}_{selected_class.section}_{selected_class.subject.name}_grades.pdf"'
            return response
        return HttpResponse('Error Rendering PDF', status=400)

    return render(request, 'teacher-CalculateGrade.html', context)













# views.py
@login_required(login_url='login')
@allowed_users(allowed_roles=['student'])
def student_subjectlist(request):
    # Get the current active school year
    try:
        current_school_year = SchoolYear.objects.get(is_active=True)
    except SchoolYear.DoesNotExist:
        return render(request, 'student-SubjectList.html', {
            'grade_level': "No active school year",
            'section': "",
            'subjects_and_teachers': [],
            'grading_periods': [],
        })

    # Get the current student's enrollments for the current school year
    student_enrollments = Enrollment.objects.filter(
        student=request.user.student,
        class_obj__school_year=current_school_year
    ).select_related('class_obj', 'class_obj__teacher', 'class_obj__subject')
    
    if student_enrollments.exists():
        # Assuming a student is enrolled in only one grade level and section per school year
        current_class = student_enrollments.first().class_obj
        grade_level = current_class.grade_level
        section = current_class.section
        
        # Get all subjects and teachers for the student's current class
        subjects_and_teachers = [
            {
                'subject': enrollment.class_obj.subject.name,
                'teacher': f"{enrollment.class_obj.teacher.Lastname}, {enrollment.class_obj.teacher.Firstname}",
                'subject_id': enrollment.class_obj.subject.id,
                'class_id': enrollment.class_obj.id
            }
            for enrollment in student_enrollments
        ]
    else:
        grade_level = "Not enrolled"
        section = "Not enrolled"
        subjects_and_teachers = []

    grading_periods = GradingPeriod.objects.filter(school_year=current_school_year)

    context = {
        'grade_level': grade_level,
        'section': section,
        'subjects_and_teachers': subjects_and_teachers,
        'grading_periods': grading_periods,
        'current_school_year': current_school_year,
    }
    return render(request, 'student-SubjectList.html', context)




#student previous classes
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .decorators import allowed_users
from .models import SchoolYear, Enrollment, GradingPeriod

@login_required(login_url='login')
@allowed_users(allowed_roles=['student'])
def student_previousClasses(request):
    student = request.user.student

    # Get all previous school years (excluding the active one)
    previous_school_years = SchoolYear.objects.filter(is_active=False)

    previous_classes = {}
    grading_periods = {}

    for school_year in previous_school_years:
        enrollments = Enrollment.objects.filter(
            student=student,
            class_obj__school_year=school_year
        ).select_related('class_obj', 'class_obj__teacher', 'class_obj__subject')

        if enrollments.exists():
            previous_classes[school_year] = enrollments
            grading_periods[school_year.id] = list(
                GradingPeriod.objects.filter(school_year=school_year)
                .values('id', 'period', 'school_year__year')  # Use school_year__year
            )

    # Convert grading_periods to JSON
    grading_periods_json = json.dumps(grading_periods)

    context = {
        'previous_classes': previous_classes,
        'grading_periods': grading_periods_json,
    }

    return render(request, 'student-PreviousClasses.html', context)



















from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Enrollment, Class, Subject, Activity, Score, GradingCriterion, GradingPeriod

@login_required(login_url='login')
@allowed_users(allowed_roles=['student'])
def student_scorelist(request):
    subject_id = request.GET.get('subject_id')
    class_id = request.GET.get('class_id')
    grading_period_id = request.GET.get('grading_period')
    
    if not subject_id or not class_id or not grading_period_id:
        messages.error(request, "Invalid subject, class, or grading period selected.")
        return redirect('student-SubjectList')
    
    try:
        subject = Subject.objects.get(id=subject_id)
        class_obj = Class.objects.get(id=class_id)
        grading_period = GradingPeriod.objects.get(id=grading_period_id)
    except (Subject.DoesNotExist, Class.DoesNotExist, GradingPeriod.DoesNotExist, ValueError):
        messages.error(request, "Invalid subject, class, or grading period selected.")
        return redirect('student-SubjectList')

    try:
        enrollment = Enrollment.objects.get(student=request.user.student, class_obj=class_obj)
    except Enrollment.DoesNotExist:
        messages.error(request, "You are not enrolled in this class.")
        return redirect('student-SubjectList')

    activities = Activity.objects.filter(
        class_obj=class_obj, 
        subject_criterion__subject=subject, 
        grading_period=grading_period
    )
    scores = Score.objects.filter(enrollment=enrollment, activity__in=activities)

    criteria = GradingCriterion.objects.all()

    score_data = []
    for activity in activities:
        score = scores.filter(activity=activity).first()
        # Only show score if the class doesn't have hidden scores
        displayed_score = None
        if score and not class_obj.hide_scores:
            displayed_score = score.score
            
        score_data.append({
            'activity_name': activity.name,
            'date': activity.date_created,
            'max_score': activity.max_score,
            'score': displayed_score,
            'criteria': activity.subject_criterion.grading_criterion.criteria_type,
            'scores_hidden': class_obj.hide_scores
        })

    context = {
        'grade_level': class_obj.grade_level,
        'section': class_obj.section,
        'subject': subject.name,
        'grading_period': grading_period.period,
        'score_data': score_data,
        'criteria': criteria,
        'scores_hidden': class_obj.hide_scores
    }
    return render(request, 'student-ScoreList.html', context)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Enrollment, Grade, GradingPeriod, SchoolYear, Subject
from django.db.models import Avg

@login_required(login_url='login')
@allowed_users(allowed_roles=['student'])
def student_reportCard(request):
    student = request.user.student
    school_years = SchoolYear.objects.all().order_by('-year')
    
    if not school_years:
        return render(request, 'student-ReportCard.html', {'error': 'No school years found.'})

    report_cards = []

    for school_year in school_years:
        enrollments = Enrollment.objects.filter(student=student, class_obj__school_year=school_year)
        
        subjects = Subject.objects.all()
        grading_periods = GradingPeriod.objects.filter(school_year=school_year).order_by('period')
        
        grades_data = {}
        for subject in subjects:
            grades_data[subject.name] = {}
            for period in grading_periods:
                grade = Grade.objects.filter(
                    enrollment__student=student,
                    enrollment__class_obj__subject=subject,
                    grading_period=period
                ).first()
                grades_data[subject.name][period.period] = grade.quarterly_grade if grade else None

        # Calculate final grades and general average
        for subject in grades_data:
            grades = [grade for grade in grades_data[subject].values() if grade is not None]
            if grades:
                grades_data[subject]['final_grade'] = round(sum(grades) / len(grades), 2)
                grades_data[subject]['remarks'] = 'Passed' if grades_data[subject]['final_grade'] >= 75 else 'Failed'
            else:
                grades_data[subject]['final_grade'] = None
                grades_data[subject]['remarks'] = None

        general_average = round(sum(subject['final_grade'] for subject in grades_data.values() if subject['final_grade'] is not None) / len(grades_data), 2) if grades_data else None

        # Determine overall pass/fail status
        overall_status = 'Passed' if general_average is not None and general_average >= 75 else 'Failed'

        grade_section = enrollments.first().class_obj.grade_level + ' - ' + enrollments.first().class_obj.section if enrollments.exists() else 'N/A'

        report_cards.append({
            'school_year': school_year,
            'grades_data': grades_data,
            'grading_periods': grading_periods,
            'general_average': general_average,
            'overall_status': overall_status,
            'grade_section': grade_section
        })

    context = {
        'student': student,
        'report_cards': report_cards,
    }

    return render(request, 'student-ReportCard.html', context)



from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from decimal import Decimal
from .models import Class, Enrollment, SubjectCriterion, Activity, Score, GradingPeriod, SchoolYear, Student

@login_required(login_url='login')
def student_InitialGrade(request):
    class_id = request.GET.get('class_id')
    grading_period_id = request.GET.get('grading_period')
    
    selected_class = get_object_or_404(Class, id=class_id)
    grading_period = get_object_or_404(GradingPeriod, id=grading_period_id) if grading_period_id else None

    # Get the Student instance associated with the current user
    student = get_object_or_404(Student, user=request.user)

    # Get the current student's enrollment
    enrollment = get_object_or_404(Enrollment, class_obj=selected_class, student=student)

    criteria = SubjectCriterion.objects.filter(subject=selected_class.subject).order_by('grading_criterion')

    current_school_year = SchoolYear.objects.filter(is_active=True).first()
    is_current_school_year = selected_class.school_year == current_school_year

    result = {
        'student': student,
        'criteria_scores': []
    }

    total_weighted_percentage = Decimal(0)

    for criterion in criteria:
        activities = Activity.objects.filter(
            class_obj=selected_class,
            subject_criterion=criterion,
            grading_period=grading_period
        )
        
        if not activities.exists():
            result['criteria_scores'].append({
                'criterion': criterion,
                'total_score': Decimal(0),
                'total_max_score': Decimal(0),
                'percentage': Decimal(0),
            })
            continue

        scores = Score.objects.filter(
            enrollment=enrollment,
            activity__in=activities
        )
        total_score = sum(score.score for score in scores)
        total_max_score = sum(activity.max_score for activity in activities)

        percentage = (Decimal(total_score) / Decimal(total_max_score) * Decimal(100)) if total_max_score > 0 else Decimal(0)
        weighted_percentage = percentage * (Decimal(criterion.weightage) / Decimal(100))
        total_weighted_percentage += weighted_percentage

        result['criteria_scores'].append({
            'criterion': criterion,
            'total_score': total_score,
            'total_max_score': total_max_score,
            'percentage': weighted_percentage,
        })

    result['initial_grade'] = total_weighted_percentage

    total_max_scores = {
        criterion.id: Activity.objects.filter(
            class_obj=selected_class,
            subject_criterion=criterion,
            grading_period=grading_period
        ).aggregate(
            total_max_score=Sum('max_score')
        )['total_max_score'] or Decimal(0)
        for criterion in criteria
    }

    context = {
        'selected_class': selected_class,
        'result': result,
        'criteria': criteria,
        'total_max_scores': total_max_scores,
        'grading_period': grading_period,
        'is_current_school_year': is_current_school_year,
    }

    return render(request, 'student-InitialGrade.html', context)





# upload grade
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Grade, Enrollment, GradingPeriod, Class, SubjectCriterion, Score, Activity
from django.db.models import Sum
from decimal import Decimal

@require_POST
def upload_grades(request):
    class_id = request.POST.get('class_id')
    grading_period_id = request.POST.get('grading_period_id')
    
    try:
        selected_class = Class.objects.get(id=class_id)
        grading_period = GradingPeriod.objects.get(id=grading_period_id)
        
        enrollments = Enrollment.objects.filter(class_obj=selected_class)
        criteria = SubjectCriterion.objects.filter(subject=selected_class.subject)
        
        for enrollment in enrollments:
            total_weighted_percentage = Decimal(0)
            
            for criterion in criteria:
                activities = Activity.objects.filter(
                    class_obj=selected_class,
                    subject_criterion=criterion,
                    grading_period=grading_period
                )
                
                if not activities.exists():
                    continue
                
                scores = Score.objects.filter(
                    enrollment=enrollment,
                    activity__in=activities
                )
                total_score = sum(score.score for score in scores)
                total_max_score = sum(activity.max_score for activity in activities)
                
                percentage = (Decimal(total_score) / Decimal(total_max_score) * Decimal(100)) if total_max_score > 0 else Decimal(0)
                weighted_percentage = percentage * (Decimal(criterion.weightage) / Decimal(100))
                total_weighted_percentage += weighted_percentage
            
            transmuted_grade = transmute_grade(total_weighted_percentage)
            
            # Create or update the Grade object
            Grade.objects.update_or_create(
                enrollment=enrollment,
                grading_period=grading_period,
                defaults={'quarterly_grade': transmuted_grade}
            )
        
        messages.success(request, 'Grades uploaded successfully!')
    except (Class.DoesNotExist, GradingPeriod.DoesNotExist) as e:
        messages.error(request, f'Error uploading grades: {str(e)}')
    
    return redirect('teacher-myClassAdvisory')




@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
@require_POST
def toggle_scores(request, class_id):
    try:
        class_obj = get_object_or_404(Class, id=class_id, teacher=request.user.teacher)
        class_obj.toggle_score_visibility()
        return JsonResponse({
            'success': True, 
            'hide_scores': class_obj.hide_scores,
            'message': f"Scores are now {'hidden' if class_obj.hide_scores else 'visible'}"
        })
    except Class.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'error': 'Class not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        }, status=500)



