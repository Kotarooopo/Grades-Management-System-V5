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
from .models import User, Class  # Import your models
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
    subjects = Subject.objects.all()  # Get all subjects

    # Get the current school year
    current_school_year = SchoolYear.objects.filter(is_active=True).first()

    context = {
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_administrators': total_administrators,
        'total_users': total_users,
        'total_sections': total_sections,
        'total_subjects': total_subjects,
        'subjects': subjects,  # Pass subjects to the template
        'current_school_year': current_school_year,  # Add the current school year to the context
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
                return redirect('admin-dashboard')
            elif user.is_teacher:
                return redirect('teacher-dashboard')
            elif user.is_student:
                return redirect('student-dashboard')
            else:
                messages.error(request, 'User role not defined.')
                return redirect('login')
        else:
            messages.error(request, 'Username or Password is incorrect')

    context = {}
    return render(request, 'login.html', context)



@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
def profile(request):
    return render(request, 'admin-profile.html')

def logoutUser(request):
    logout(request)
    return redirect('login')



#edit-profile admin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import AdministratorForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
@allowed_users(allowed_roles=['administrator'])
def profile(request):
    admin = request.user.administrator

    if request.method == 'POST':
        if 'current_password' in request.POST:
            change_form = PasswordChangeForm(request.POST)
            form = AdministratorForm(instance=admin)
            if change_form.is_valid():
                current_password = change_form.cleaned_data['current_password']
                new_password = change_form.cleaned_data['new_password']
                
                if not request.user.check_password(current_password):
                    messages.error(request, 'Current password is incorrect')
                else:
                    user = request.user
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)  # Important!
                    messages.success(request, 'Your password was successfully updated!')
                    return redirect('admin-profile')  # Redirect to the profile page
        else:
            form = AdministratorForm(request.POST, request.FILES, instance=admin)
            change_form = PasswordChangeForm()
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('admin-profile')  # Redirect to the profile page
    else:
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
                    messages.error(request, 'Current password is incorrect')
                else:
                    user = request.user
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)  # Important!
                    messages.success(request, 'Your password was successfully updated!')
                    return redirect('teacher-profile')  # Redirect to the profile page
        else:
            form = TeacherForm(request.POST, request.FILES, instance=teacher)
            change_form = PasswordChangeForm()
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('teacher-profile')  # Redirect to the profile page
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
@allowed_users(allowed_roles=['student'])
def student_profile(request):
    student = request.user.student

    if request.method == 'POST':
        if 'current_password' in request.POST:
            change_form = PasswordChangeForm(request.POST)
            form = StudentForm(instance=student)
            if change_form.is_valid():
                current_password = change_form.cleaned_data['current_password']
                new_password = change_form.cleaned_data['new_password']
                
                if not request.user.check_password(current_password):
                    messages.error(request, 'Current password is incorrect')
                else:
                    user = request.user
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)  # Important!
                    messages.success(request, 'Your password was successfully updated!')
                    return redirect('student-profile')  # Redirect to the profile page
        else:
            form = StudentForm(request.POST, request.FILES, instance=student)
            change_form = PasswordChangeForm()
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('student-profile')  # Redirect to the profile page
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


@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully')
            return redirect('login')  # Redirect to login page after successful registration
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
from .models import Class, Enrollment, SubjectCriterion, Activity, Score, GradingPeriod, SchoolYear
import json

@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def teacher_dashboard(request):
    teacher = request.user.teacher
    current_school_year = SchoolYear.objects.filter(is_active=True).first()

    # Filter classes based on the current school year
    classes = Class.objects.filter(teacher=teacher, school_year=current_school_year)
    class_data = classes.annotate(student_count=Count('enrollments__student')).values('section', 'student_count')

    sections = [class_info['section'] for class_info in class_data]
    student_counts = [class_info['student_count'] for class_info in class_data]

    selected_section = request.GET.get('section', sections[0] if sections else None)
    
    grading_periods = GradingPeriod.objects.all().order_by('id')
    first_grading = grading_periods.first()
    selected_grading_period_id = request.GET.get('grading_period', first_grading.id if first_grading else None)
    
    if selected_grading_period_id:
        selected_grading_period = GradingPeriod.objects.get(id=selected_grading_period_id)
    else:
        selected_grading_period = first_grading

    top_students = get_top_students(teacher, selected_section, selected_grading_period, current_school_year, limit=5) if selected_section else []

    # Get all enrollments for the teacher's classes
    all_enrollments = Enrollment.objects.filter(class_obj__teacher=teacher, class_obj__school_year=current_school_year).select_related('student', 'class_obj')

    total_students = all_enrollments.count()
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
        'selected_grading_period': selected_grading_period,
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









@login_required(login_url='login')
@allowed_users(allowed_roles=['student'])
def student_dashboard(request):
    return render(request, 'student-dashboard.html')




#teacher-list
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .decorators import allowed_users
from .models import Teacher, Administrator, Class

@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
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
        
        elif 'toggle_status' in request.POST:
            toggle_status_id = request.POST.get('toggle_status_id')
            current_status = request.POST.get('current_status')

            user = get_object_or_404(User, id=toggle_status_id)
            if current_status == 'active':
                user.is_active = False
                messages.success(request, f"Account for {user.email} has been deactivated successfully.")
            else:
                user.is_active = True
                messages.success(request,f"Account for {user.email} has been activated successfully.")
            user.save()

        return redirect('teacher-list')

    teachers = Teacher.objects.all()
    return render(request, 'admin-TeacherList.html', {'teachers': teachers})



from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from .models import Student

User = get_user_model()

@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
def student_list(request):
    if request.method == 'POST':
        if 'change_pass' in request.POST:
            edit_id = request.POST.get('edit_id')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password and confirm_password:
                if new_password != confirm_password:
                    messages.error(request, "Passwords do not match.")
                    return redirect('student-list')

                user = get_object_or_404(User, id=edit_id)
                user.password = make_password(new_password)
                user.save()
                messages.success(request, "Password updated successfully.")
            else:
                messages.error(request, "Please fill in both password fields.")
        
        elif 'deactivate_account' in request.POST:
            deactivate_id = request.POST.get('deactivate_id')
            user = get_object_or_404(User, id=deactivate_id)
            user.is_active = False
            user.save()
            messages.success(request, f"Account for {user.email} has been deactivated.")


        elif 'toggle_status' in request.POST:
            toggle_status_id = request.POST.get('toggle_status_id')
            current_status = request.POST.get('current_status')
            user = get_object_or_404(User, id=toggle_status_id)
            user.is_active = not user.is_active
            user.save()
            action = "activated" if user.is_active else "deactivated"
            messages.success(request, f"Account for {user.email} has been {action}.")

        return redirect('student-list')

    students = Student.objects.all()
    return render(request, 'admin-StudentList.html', {'students': students})


@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
def administrator_list(request):
    administrator = Administrator.objects.all()
    return render(request, 'admin-AdminList.html', {'administrator': administrator})



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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
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
                messages.success(request, 'School Year deleted successfully.')
            except SchoolYear.DoesNotExist:
                messages.error(request, 'School Year not found.')
            return redirect('admin-SY')
        
        year_id = request.POST.get('edit_id')
        if year_id:
            # Editing existing school year
            school_year = get_object_or_404(SchoolYear, id=year_id)
            form = SchoolYearForm(request.POST, instance=school_year)
            success_message = 'School Year updated successfully!'
            error_message = 'Error updating School Year. Please check the form.'
        else:
            # Adding new school year
            form = SchoolYearForm(request.POST)
            success_message = 'School Year added successfully!'
            error_message = 'Error adding School Year. Please check the form.'
        
        if form.is_valid():
            form.save()
            messages.success(request, success_message)
        else:
            messages.error(request, error_message)
        
        return redirect('admin-SY')
    else:
        form = SchoolYearForm()
    
    context = {
        'years': years,
        'form': form,
    }
    return render(request, 'admin-SchoolYear.html', context)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Enrollment, Grade, GradingPeriod, SchoolYear, Subject, Student

@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
def admin_GradeReport(request):
    students = Student.objects.all()
    school_years = SchoolYear.objects.all().order_by('-year')
    
    if not school_years.exists():
        return render(request, 'admin-GradeReport.html', {'error': 'No school years found.'})

    subjects = Subject.objects.all()

    report_cards = []

    for student in students:
        for school_year in school_years:
            enrollments = Enrollment.objects.filter(student=student, class_obj__school_year=school_year)
            grading_periods = GradingPeriod.objects.filter(school_year=school_year).order_by('period')
            
            grades_data = {}
            for subject in subjects:
                grades_data[subject.name] = {'quarterly_grades': {}}
                for period in grading_periods:
                    grade = Grade.objects.filter(
                        enrollment__student=student,
                        enrollment__class_obj__subject=subject,
                        grading_period=period
                    ).first()
                    grades_data[subject.name]['quarterly_grades'][period.period] = grade.quarterly_grade if grade else None

                # Calculate final grade
                quarterly_grades = [grade for grade in grades_data[subject.name]['quarterly_grades'].values() if grade is not None]
                if quarterly_grades:
                    final_grade = round(sum(quarterly_grades) / len(quarterly_grades), 2)
                    grades_data[subject.name]['final_grade'] = final_grade
                    grades_data[subject.name]['remarks'] = 'Passed' if final_grade >= 75 else 'Failed'
                else:
                    grades_data[subject.name]['final_grade'] = None
                    grades_data[subject.name]['remarks'] = None

            general_average = round(sum(subject['final_grade'] for subject in grades_data.values() if subject['final_grade'] is not None) / len(grades_data), 2) if grades_data else None

            grade_section = enrollments.first().class_obj.grade_level + ' - ' + enrollments.first().class_obj.section if enrollments.exists() else 'N/A'

            report_cards.append({
                'student': student,
                'school_year': school_year,
                'grades_data': grades_data,
                'grading_periods': grading_periods,
                'general_average': general_average,
                'grade_section': grade_section
            })

    context = {
        'report_cards': report_cards,
    }

    return render(request, 'admin-GradeReport.html', context)




from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SchoolYear, GradingPeriod

@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
def admin_GradingPeriod(request):
    current_school_year = SchoolYear.objects.filter(is_active=True).first()
    grading_periods = GradingPeriod.objects.filter(school_year=current_school_year).order_by('period') if current_school_year else []

    if request.method == 'POST':
        if 'add_grading_period' in request.POST:
            period = request.POST.get('period')
            is_current = request.POST.get('is_current') == 'True'
            
            if current_school_year:
                GradingPeriod.objects.create(
                    school_year=current_school_year,
                    period=period,
                    is_current=is_current
                )
                messages.success(request, 'Grading Period added successfully.')
            else:
                messages.error(request, 'No active school year found.')

        elif 'edit_grading_period' in request.POST:
            grading_period_id = request.POST.get('edit_id')
            is_current = request.POST.get('is_current') == 'True'
            
            grading_period = GradingPeriod.objects.get(id=grading_period_id)
            grading_period.is_current = is_current
            grading_period.save()
            messages.success(request, 'Grading Period updated successfully.')

        elif 'delete_grading_period' in request.POST:
            grading_period_id = request.POST.get('delete_id')
            GradingPeriod.objects.filter(id=grading_period_id).delete()
            messages.success(request, 'Grading Period deleted successfully.')

        return redirect('admin-GradingPeriod')

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
from django.db.models import Q
from .forms import AddClassForm
from .models import Class, SchoolYear, Subject, Teacher
from .models import GradingPeriod

@login_required(login_url='login')
@allowed_users(allowed_roles=['administrator'])
def admin_class(request):
    current_school_year = SchoolYear.objects.filter(is_active=True).first()
    
    current_classes = Class.objects.filter(school_year=current_school_year).order_by('grade_level', 'section')
    previous_classes = Class.objects.filter(~Q(school_year=current_school_year)).order_by('-school_year__year', 'grade_level', 'section')
    
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
        'previous_classes': previous_classes,
        'current_school_year': current_school_year,
        'active_school_years': active_school_years,
        'teachers': teachers,
        'subjects': subjects,
    }
    return render(request, 'admin-Class.html', context)




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
    
    # Fetch the selected class
    selected_class = get_object_or_404(Class, id=selected_class_id)
    
    # Fetch the selected grading period
    grading_period = get_object_or_404(GradingPeriod, period=selected_grading_period, school_year=selected_class.school_year)
    
    # Fetch activities based on selected criteria, class, and grading period
    activities = Activity.objects.filter(
        class_obj=selected_class,
        subject_criterion__grading_criterion__criteria_type=selected_criteria,
        grading_period=grading_period
    ).order_by('date_created')
    
    # Fetch enrollments for the selected class
    enrollments = Enrollment.objects.filter(class_obj=selected_class)
    
    scores_data = []
    for enrollment in enrollments:
        student_scores = []
        for activity in activities:
            score = Score.objects.filter(enrollment=enrollment, activity=activity).first()
            student_scores.append({
                'activity_name': activity.name,
                'date_created': activity.date_created.strftime('%Y-%m-%d'),
                'score': score.score if score else 0,
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
        'students': Student.objects.filter(enrollments__class_obj=selected_class) if selected_class else []
    }

    return render(request, 'teacher-ClassRecord.html', context)


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Enrollment

@csrf_exempt
def remove_student(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            enrollment_id = data.get('enrollment_id')
            if not enrollment_id:
                return JsonResponse({'success': False, 'error': 'Missing enrollment_id'}, status=400)
            
            # Debugging log to check the value of enrollment_id
            print(f'Received enrollment_id: {enrollment_id}')

            enrollment = get_object_or_404(Enrollment, id=enrollment_id)
            enrollment.delete()
            return JsonResponse({'success': True})
        except json.JSONDecodeError as e:
            return JsonResponse({'success': False, 'error': 'Invalid JSON: ' + str(e)}, status=400)
        except Exception as e:
            # Log the error for debugging
            print(f"Error in remove_student view: {e}")
            return JsonResponse({'success': False, 'error': 'An error occurred: ' + str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


 




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

    activities = Activity.objects.filter(class_obj=class_obj, subject_criterion__subject=subject, grading_period=grading_period)
    scores = Score.objects.filter(enrollment=enrollment, activity__in=activities)

    criteria = GradingCriterion.objects.all()

    score_data = []
    for activity in activities:
        score = scores.filter(activity=activity).first()
        score_data.append({
            'activity_name': activity.name,
            'date': activity.date_created,
            'max_score': activity.max_score,
            'score': score.score if score else None,
            'criteria': activity.subject_criterion.grading_criterion.criteria_type
        })

    context = {
        'grade_level': class_obj.grade_level,
        'section': class_obj.section,
        'subject': subject.name,
        'grading_period': grading_period.period,
        'score_data': score_data,
        'criteria': criteria,
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
