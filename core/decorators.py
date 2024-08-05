from django.http import HttpResponse
from django.shortcuts import redirect

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_administrator:
                return redirect('admin-dashboard')
            elif request.user.is_teacher:
                return redirect('teacher-dashboard')
            elif request.user.is_student:
                return redirect('student-dashboard')
            else:
                return redirect('login')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if 'administrator' in allowed_roles and request.user.is_administrator:
                return view_func(request, *args, **kwargs)
            elif 'teacher' in allowed_roles and request.user.is_teacher:
                return view_func(request, *args, **kwargs)
            elif 'student' in allowed_roles and request.user.is_student:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('You are not authorized to view this page')
        return wrapper_func
    return decorator

def role_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.is_administrator:
                return redirect('admin-dashboard')
            elif user.is_teacher:
                return redirect('teacher-dashboard')
            elif user.is_student:
                return redirect('student-dashboard')
            else:
                return redirect('home')
        else:
            return redirect('login')
    return wrapper_func
