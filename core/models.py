from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import os
import uuid
from PIL import Image
from django.db import IntegrityError
from django.conf import settings 
import logging

from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)
def resize_image(image, size=(300, 300)):
    if image and hasattr(image, 'path') and os.path.isfile(image.path):
        try:
            img = Image.open(image.path)
            img.thumbnail(size)
            img_format = img.format
            img.save(image.path, img_format)
        except Exception as e:
            logger.error(f"Error resizing image: {str(e)}")

def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('core/images', filename)



# new
class SchoolYear(models.Model):
    year = models.CharField(max_length=9, unique=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.year

    def save(self, *args, **kwargs):
        if self.is_active:
            # Check if there's already an active school year
            active_year = SchoolYear.objects.filter(is_active=True).exclude(pk=self.pk).first()
            if active_year:
                # If there's an active year, deactivate it
                active_year.is_active = False
                active_year.save()
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "School Years"
    
class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



class Administrator(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    user = models.OneToOneField('User', on_delete=models.CASCADE, primary_key=True)
    Firstname = models.CharField(max_length=200, null=True)
    Lastname = models.CharField(max_length=200, null=True)
    Middle_Initial = models.CharField(max_length=10, null=True, blank=True)
    Gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    Phone_Number = models.CharField(max_length=11, null=True, blank=True)
    profile_picture = models.ImageField(upload_to=user_directory_path, default='media/default_profile.png', blank=True)

    def save(self, *args, **kwargs):
        if self.profile_picture:
            resize_image(self.profile_picture)
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.Firstname} {self.Lastname}"
    #new
    def create_school_year(self, year):
        return SchoolYear.objects.create(year=year)

    def create_subject(self, name, school_year):
        return Subject.objects.create(name=name, school_year=school_year)

    def create_class(self, subject, grade_level, section, teacher, school_year):
        return Class.objects.create(
            subject=subject,
            grade_level=grade_level,
            section=section,
            teacher=teacher,
            school_year=school_year
        )
    def assign_teacher_to_class(self, teacher, class_obj):
        class_obj.teacher = teacher
        class_obj.save()
    @property
    def email(self):
        return self.user.email


class Class(models.Model):
    GradeLvl_Choices = [
        ('Grade 7', 'Grade 7'),
        ('Grade 8', 'Grade 8'),
        ('Grade 9', 'Grade 9'),
        ('Grade 10', 'Grade 10'),
    ]
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='classes')
    grade_level = models.CharField(max_length=50, choices=GradeLvl_Choices)
    section = models.CharField(max_length=50)
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE, null=True, blank=True,)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='classes', null=True, blank=True)
    hide_scores = models.BooleanField(default=False)

    class Meta:
        unique_together = ('school_year', 'grade_level', 'section', 'subject')
    def __str__(self):
        subject_name = self.subject.name if self.subject else "No subject"
        teacher_name = self.teacher.Lastname if self.teacher else "No Teacher Assigned"
        return f"({self.school_year.year}) {self.grade_level} {self.section} - Teacher {teacher_name} - Class {subject_name}"
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def toggle_score_visibility(self):
        self.hide_scores = not self.hide_scores
        self.save()
    



from django.db import models
from django.core.exceptions import ValidationError
from django.db import IntegrityError

class Enrollment(models.Model):
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='enrollments')

    class Meta:
        indexes = [
            models.Index(fields=['student', 'class_obj']),
        ]

    def __str__(self):
        return f"{self.student.Lastname} enrolled in {self.class_obj}"

    def clean(self):
        if self.pk is None:  # Only check on creation, not on update
            # Check for existing enrollment in the same school year, grade level, and section but different subjects
            existing_enrollment_same_grade_and_section = Enrollment.objects.filter(
                student=self.student,
                class_obj__school_year=self.class_obj.school_year,
                class_obj__grade_level=self.class_obj.grade_level,
                class_obj__section=self.class_obj.section,
            ).exists()
            
            # Check for existing enrollment in the same school year, grade level, section, and subject
            existing_enrollment_same_subject = Enrollment.objects.filter(
                student=self.student,
                class_obj__school_year=self.class_obj.school_year,
                class_obj__grade_level=self.class_obj.grade_level,
                class_obj__section=self.class_obj.section,
                class_obj__subject=self.class_obj.subject
            ).exists()


            if existing_enrollment_same_subject:
                raise ValidationError("Student is already enrolled in a class with this grade level, section, and subject in the same school year.")
            else:
                # Check for existing enrollment in a different grade level or section within the same school year
                existing_enrollment_different_grade_or_section = Enrollment.objects.filter(
                    student=self.student,
                    class_obj__school_year=self.class_obj.school_year
                ).exclude(
                    class_obj__grade_level=self.class_obj.grade_level,
                    class_obj__section=self.class_obj.section
                ).exists()

                if existing_enrollment_different_grade_or_section:
                    raise ValidationError("Student cannot be enrolled in different grade levels or sections within the same school year.")

    def save(self, *args, **kwargs):
        self.clean()  # This will raise ValidationError if the clean method fails
        super().save(*args, **kwargs)
    pass




class Teacher(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    user = models.OneToOneField('User', on_delete=models.CASCADE, primary_key=True)
    Firstname = models.CharField(max_length=200, null=True)
    Lastname = models.CharField(max_length=200, null=True)
    Middle_Initial = models.CharField(max_length=10, null=True, blank=True)
    Gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    Phone_Number = models.CharField(max_length=11, null=True, blank=True)

    profile_picture = models.ImageField(upload_to=user_directory_path, default='core/images/default_profile.png', blank=True)
    
    def save(self, *args, **kwargs):
        if self.profile_picture:
            resize_image(self.profile_picture)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.Firstname} {self.Lastname}"
    
    @property
    def name(self):
        return f"{self.Firstname} {self.Lastname}"
    
    def add_student_to_class(self, student, class_obj):
        if class_obj in self.classes.all():
            try:
                Enrollment.objects.create(student=student, class_obj=class_obj)
            except IntegrityError:
                raise ValueError(f"{student.Lastname} is already enrolled in {class_obj}.")
        else:
            raise ValueError("This teacher is not assigned to this class.")

    def set_current_grading_period(self, class_obj, grading_period):
        if class_obj in self.classes.all():
            GradingPeriod.objects.filter(school_year=class_obj.school_year).update(is_current=False)
            grading_period.is_current = True
            grading_period.save()
        else:
            raise ValueError("This teacher is not assigned to this class.")

    def set_grading_criteria(self, subject, criteria_type, weight):
        if subject in self.classes.values_list('subject', flat=True):
            GradingCriterion.objects.update_or_create(
                subject=subject,
                criteria_type=criteria_type,
                defaults={'weight': weight}
            )
        else:
            raise ValueError("This teacher is not assigned to this subject.")

    def add_score(self, student, class_obj, criteria_type, score, max_score):
        if class_obj in self.classes.all():
            current_grading_period = GradingPeriod.objects.get(school_year=class_obj.school_year, is_current=True)
            criteria = GradingCriterion.objects.get(subject=class_obj.subject, criteria_type=criteria_type)
            enrollment = Enrollment.objects.get(student=student, class_obj=class_obj)
            Score.objects.create(
                enrollment=enrollment,
                grading_period=current_grading_period,
                subject_criterion=criteria,
                score=score,
                max_score = max_score, 
                score_date=current_grading_period.date # Assuming date is part of GradingPeriod model
            )
        else:
            raise ValueError("This teacher is not assigned to this class.")

    def calculate_grades(self, class_obj):
        if class_obj in self.classes.all():
            current_grading_period = GradingPeriod.objects.get(school_year=class_obj.school_year, is_current=True)
            enrollments = Enrollment.objects.filter(class_obj=class_obj)
            for enrollment in enrollments:
                scores = Score.objects.filter(
                    enrollment=enrollment,
                    grading_period=current_grading_period
                )
                total_weighted_score = 0
                for score in scores:
                    criteria_weight = score.subject_criterion.weightage / 100  # Convert percentage to decimal
                    weighted_score = (score.score / score.subject_criterion.max_score) * criteria_weight
                    total_weighted_score += weighted_score

                initial_grade = total_weighted_score * 100  # Convert back to percentage
                final_grade = self.convert_to_final_grade(initial_grade)

        else:
            raise ValueError("This teacher is not assigned to this class.")
        
    def hide_class_scores(self, class_obj):
        """Hide scores for a specific class"""
        if class_obj in self.classes.all():
            class_obj.hide_scores = True
            class_obj.save()
        else:
            raise ValueError("This teacher is not assigned to this class.")

    def show_class_scores(self, class_obj):
        """Show scores for a specific class"""
        if class_obj in self.classes.all():
            class_obj.hide_scores = False
            class_obj.save()
        else:
            raise ValueError("This teacher is not assigned to this class.")

    def toggle_class_scores(self, class_obj):
        """Toggle score visibility for a specific class"""
        if class_obj in self.classes.all():
            class_obj.toggle_score_visibility()
        else:
            raise ValueError("This teacher is not assigned to this class.")


    @property
    def email(self):
        return self.user.email

        
class Student(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    user = models.OneToOneField('User', on_delete=models.CASCADE, primary_key=True)
    Firstname = models.CharField(max_length=200, null=True)
    Lastname = models.CharField(max_length=200, null=True)
    Middle_Initial = models.CharField(max_length=10, null=True, blank=True)
    Gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    Phone_Number = models.CharField(max_length=11, null=True, blank=True)

    profile_picture = models.ImageField(upload_to=user_directory_path, default='core/images/default_profile.png', blank=True)
    def save(self, *args, **kwargs):
        if self.profile_picture:
            resize_image(self.profile_picture)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.Firstname} {self.Lastname}"
    

    def get_full_name(self):
        return f"{self.Lastname}, {self.Firstname}"
    
    @property
    def email(self):
        return self.user.email









    


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_administrator(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_administrator', True)
        return self.create_user(email, password, **extra_fields)

    def create_teacher(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_teacher', True)
        return self.create_user(email, password, **extra_fields)

    def create_student(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_student', True)
        return self.create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_administrator = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    


#NEW
class GradingPeriod(models.Model):
    PERIOD_CHOICES = [
        ('1st', '1st Grading'),
        ('2nd', '2nd Grading'),
        ('3rd', '3rd Grading'),
        ('4th', '4th Grading'),
    ]
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='grading_periods')
    period = models.CharField(max_length=3, choices=PERIOD_CHOICES)
    is_current = models.BooleanField(default=False)

    class Meta:
        unique_together = ('school_year', 'period')

    def __str__(self):
        return f"{self.school_year.year} - {self.get_period_display()}"

from decimal import Decimal
from django.db import models, transaction
from django.db.models import F, Sum, Q
from django.core.exceptions import ValidationError

class GradingCriterion(models.Model):
    CRITERIA_CHOICES = [
        ('WW', 'Written Works'),
        ('PT', 'Performance Tasks'),
        ('QE', 'Quarterly Exam'),
    ]
    criteria_type = models.CharField(max_length=2, choices=CRITERIA_CHOICES)

    def __str__(self):
        return f"{self.get_criteria_type_display()}"

class SubjectCriterion(models.Model):
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    grading_criterion = models.ForeignKey(GradingCriterion, on_delete=models.CASCADE)
    weightage = models.IntegerField()

    class Meta:
        unique_together = ('subject', 'grading_criterion')

    def __str__(self):
        return f"{self.subject.name} - {self.grading_criterion.get_criteria_type_display()} - {self.weightage}%"

    def clean(self):
        if not self.pk:
            if SubjectCriterion.objects.filter(subject=self.subject, grading_criterion=self.grading_criterion).exists():
                raise ValidationError("This grading criterion is already defined for this subject.")

        total_weightage = SubjectCriterion.objects.filter(subject=self.subject).exclude(pk=self.pk).aggregate(Sum('weightage'))['weightage__sum'] or 0
        total_weightage += self.weightage

        criteria_count = SubjectCriterion.objects.filter(subject=self.subject).count()
        if not self.pk:
            criteria_count += 1

        if criteria_count > 3:
            raise ValidationError("A subject can have a maximum of 3 criteria.")
        elif criteria_count == 3 and total_weightage != 100:
            raise ValidationError(f"The total weightage for all three criteria of a subject must be exactly 100%. Current total: {total_weightage}%")
        elif total_weightage > 100:
            raise ValidationError(f"The total weightage cannot exceed 100%. Current total: {total_weightage}%")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @classmethod
    def get_total_weightage(cls, subject):
        return cls.objects.filter(subject=subject).aggregate(Sum('weightage'))['weightage__sum'] or 0

class Activity(models.Model):
    class_obj = models.ForeignKey('Class', on_delete=models.CASCADE)
    grading_period = models.ForeignKey(
        'GradingPeriod', 
        on_delete=models.CASCADE, 
        null=True,
    )
    name = models.CharField(max_length=100)
    subject_criterion = models.ForeignKey(SubjectCriterion, on_delete=models.CASCADE)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject_criterion} - {self.max_score} points"

    def clean(self):
        super().clean()
        if self.subject_criterion.subject != self.class_obj.subject:
            raise ValidationError("The subject criterion must match the class subject.")
        if self.grading_period and not self.grading_period.is_current:
            raise ValidationError("Only current grading periods can be selected.")
        if not self.id and Activity.objects.filter(class_obj=self.class_obj, subject_criterion=self.subject_criterion, name=self.name).exists():
            raise ValidationError("An activity with this name already exists for this class and subject criterion.")

    def create_initial_scores(self):
        from .models import Score, Enrollment
        enrollments = Enrollment.objects.filter(class_obj=self.class_obj)
        scores_to_create = [Score(enrollment=enrollment, activity=self) for enrollment in enrollments]
        Score.objects.bulk_create(scores_to_create)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        self.full_clean()
        with transaction.atomic():
            super().save(*args, **kwargs)
            if is_new:
                self.create_initial_scores()

from decimal import Decimal
from django.db.models import F, Sum
from django.core.exceptions import ValidationError
from django.db import models, transaction

class Score(models.Model):  
    enrollment = models.ForeignKey('Enrollment', on_delete=models.CASCADE, null=True)
    activity = models.ForeignKey('Activity', on_delete=models.CASCADE, null=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    class Meta:
        unique_together = ['enrollment', 'activity']

    def __str__(self):
        student_name = self.enrollment.student.Lastname if self.enrollment.student else "Unknown Student"
        return f"{student_name} - {self.activity.name} - {self.score}/{self.activity.max_score}"

    def clean(self):
        super().clean()
        if self.activity.subject_criterion.subject != self.enrollment.class_obj.subject:
            raise ValidationError("Activity's subject criterion does not match the subject of the class.")
        if self.score > self.activity.max_score:
            raise ValidationError(f"Score cannot be higher than the max score ({self.activity.max_score}) for the activity.")

    def calculate_weighted_score(self):
        percentage = (self.score / self.activity.max_score) * 100
        weightage = self.activity.subject_criterion.weightage
        return Decimal((percentage * weightage) / 100).quantize(Decimal('0.01'))
    
    def is_visible_to_student(self, student):
        """Check if the score should be visible to the student"""
        if student != self.enrollment.student:
            return False
        return not self.enrollment.class_obj.hide_scores

    def get_display_score(self, student):
        """Get the score value based on visibility settings"""
        if self.is_visible_to_student(student):
            return self.score
        return None

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.update_total_initial_grade()

    def update_total_initial_grade(self):
        subject = self.activity.subject_criterion.subject
        enrollment = self.enrollment
        
        total_grade = Score.objects.filter(
            enrollment=enrollment,
            activity__subject_criterion__subject=subject
        ).select_related('activity__subject_criterion').aggregate(
            total=Sum(F('score') / F('activity__max_score') * F('activity__subject_criterion__weightage'))
        )['total'] or 0


class Grade(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    grading_period = models.ForeignKey(GradingPeriod, on_delete=models.CASCADE)
    quarterly_grade = models.DecimalField(max_digits=5, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('enrollment', 'grading_period')

    def __str__(self):
        return f"{self.enrollment.student.get_full_name()} - {self.grading_period} - {self.quarterly_grade}"







