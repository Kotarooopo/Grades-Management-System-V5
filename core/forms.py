from django import forms
from .models import Administrator, User, Teacher, Student

class AdministratorForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Administrator
        fields = ['Firstname', 'Lastname', 'Middle_Initial', 'Gender', 'Phone_Number', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        administrator = super().save(commit=False)
        if commit:
            # Save the Administrator instance
            administrator.save()
            
            # Update the email in the User model
            user = administrator.user
            user.email = self.cleaned_data['email']
            user.save()
        
        return administrator
    




#teacher
class TeacherForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Teacher
        fields = ['Firstname', 'Lastname', 'Middle_Initial', 'Gender', 'Phone_Number', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        teacher = super().save(commit=False)
        if commit:
            # Save the Teacher instance
            teacher.save()
            
            # Update the email in the User model
            user = teacher.user
            user.email = self.cleaned_data['email']
            user.save()
        
        return teacher



#student
class StudentForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Student
        fields = ['Firstname', 'Lastname', 'Middle_Initial', 'Gender', 'Phone_Number', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        student = super().save(commit=False)
        if commit:
            # Save the Student instance
            student.save()
            
            # Update the email in the User model
            user = student.user
            user.email = self.cleaned_data['email']
            user.save()
        
        return student




    

#change password
from django import forms

class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300'}),
        label='Current Password'
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300'}),
        label='New Password'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300'}),
        label='Confirm Password'
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("New passwords do not match")
        return cleaned_data

# register

from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import User, Administrator, Teacher, Student

class UserRegistrationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    role = forms.ChoiceField(choices=[('admin', 'Admin'), ('student', 'Student'), ('teacher', 'Teacher')])
    first_name = forms.CharField(max_length=200)
    middle_name = forms.CharField(max_length=200, required=False)
    last_name = forms.CharField(max_length=200)
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')])
    phone_number = forms.CharField(max_length=11)
    profile_picture = forms.ImageField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        try:
            validate_password(password)
        except forms.ValidationError as error:
            self.add_error('password', error)

        # Check if email already exists
        if User.objects.filter(email=cleaned_data.get('email')).exists():
            raise forms.ValidationError("This email is already in use.")

        return cleaned_data

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            email=data['email'],
            password=data['password']
        )

        profile_data = {
            'user': user,
            'Firstname': data['first_name'],
            'Lastname': data['last_name'],
            'Middle_Initial': data['middle_name'],
            'Gender': data['gender'],
            'Phone_Number': data['phone_number'],
            'profile_picture': data['profile_picture'],
        }

        if data['role'] == 'admin':
            user.is_administrator = True
            Administrator.objects.create(**profile_data)
        elif data['role'] == 'teacher':
            user.is_teacher = True
            Teacher.objects.create(**profile_data)
        elif data['role'] == 'student':
            user.is_student = True
            Student.objects.create(**profile_data)

        user.save()
        return user
    
#school year
from django import forms
from .models import SchoolYear

class SchoolYearForm(forms.ModelForm):
    class Meta:
        model = SchoolYear
        fields = ['year', 'is_active']
        widgets = {
            'year': forms.TextInput(attrs={'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'}),
            'is_active': forms.Select(attrs={'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'}),
        }


#subect
from django import forms
from .models import Subject

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white',
                'placeholder': 'Mathematics'
            })
        }



#Class
from django import forms
from .models import Class, Subject, Teacher, SchoolYear

class AddClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['school_year', 'grade_level', 'section', 'teacher', 'subject']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school_year'].queryset = SchoolYear.objects.filter(is_active=True)
        self.fields['teacher'].queryset = Teacher.objects.all()
        self.fields['subject'].queryset = Subject.objects.all()
        
        # Make fields required
        self.fields['school_year'].required = True
        self.fields['grade_level'].required = True
        self.fields['section'].required = True
        self.fields['teacher'].required = True
        self.fields['subject'].required = True
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-select'})




#add student to class
class AddStudentForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=forms.HiddenInput()
    )

#add score to a student
from django import forms
from .models import Score, Activity, Enrollment

class AddScoreForm(forms.ModelForm):
    activity = forms.ModelChoiceField(queryset=Activity.objects.none())
    enrollment = forms.ModelChoiceField(queryset=Enrollment.objects.none())
    
    class Meta:
        model = Score
        fields = ['activity', 'enrollment', 'score']

    def __init__(self, *args, **kwargs):
        class_obj = kwargs.pop('class_obj', None)
        super().__init__(*args, **kwargs)
        if class_obj:
            self.fields['activity'].queryset = Activity.objects.filter(class_obj=class_obj)
            self.fields['enrollment'].queryset = Enrollment.objects.filter(class_obj=class_obj)