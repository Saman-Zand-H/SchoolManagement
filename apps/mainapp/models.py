from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import Permission, Group
from django.db.models import Avg
from django.core.exceptions import ValidationError
from django.conf import settings
from django.urls import reverse
from ckeditor.fields import RichTextField

from datetime import date
from dateutil.relativedelta import relativedelta
from statistics import mean
from logging import getLogger

from teachers.models import Teacher
from supports.models import School

logger = getLogger(__name__)


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name="student_user",
                                on_delete=models.CASCADE)
    student_class = models.ForeignKey("Class",
                                      on_delete=models.SET_NULL,
                                      null=True,
                                      related_name="student_class",
                                      verbose_name="Student Class",
                                      blank=True)
    
    class Meta:
        permissions = (
            ("student", "Student"),
        )

    def __str__(self):
        return self.user.username
    
    def __repr__(self):
        return f"<Student: {self.user.username}>"

    def get_absolute_url_supports(self):
        return reverse("supports:students-detail", kwargs={"pk": self.pk})

    def get_absolute_url_teachers(self):
        return reverse("teachers:students-detail", kwargs={"pk": self.pk})
    
    def save(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name="Students")
        if created:
            group.permissions.add(
                Permission.objects.get(codename="student"))
        self.user.groups.add(group)
        return super().save(*args, **kwargs) 
    
    @property
    def average_grade_percent(self):
        return mean([
            grade.grade_percent for grade 
            in self.grade_user.all()
        ]) if self.grade_user.exists() else 0
    
    def _average_grade_percent_during_a_month(self, date_time):
        filter_month = date_time.month
        filter_year = date_time.year
        grades = self.grade_user.filter(exam__timestamp__month=filter_month,
                                       exam__timestamp__year=filter_year)
        percents = [grade.grade_percent for grade in grades]
        return round(mean(percents)) if grades.exists() else 0
    
    def average_grade_percent_during_eigth_months(self): 
        init_date = date.today() - relativedelta(months=4)
        percents = []
        for i in range(8):
            month = init_date + relativedelta(months=i)
            percent = self._average_grade_percent_during_a_month(month)
            percents.append(percent)
        return percents
        
    def clean(self):
        super().clean()
        if self.user.user_type != "S":
            raise ValidationError({"user": "User is not a student."})


class Subject(models.Model):
    name = models.CharField(max_length=30)
    teacher = models.ForeignKey(Teacher,
                                on_delete=models.CASCADE,
                                related_name="subject_teacher")

    def __str__(self):
        return f"{self.name} - {self.teacher}"
    
    def __repr__(self):
        return f"<Subject: ({self.teacher.user.username}-{self.name})>"

    def get_absolute_url(self):
        return reverse("supports:subjects-detail", kwargs={"pk": self.pk})

    class Meta:
        unique_together = ["name", "teacher"]
        verbose_name = "Course"
        verbose_name_plural = "Courses"

class Grade(models.Model):
    student = models.ForeignKey(Student,
                                on_delete=models.CASCADE,
                                related_name="grade_user")
    grade = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        null=True,
        blank=True,
    )
    exam = models.ForeignKey("Exam",
                             related_name="grade_exam",
                             on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student}, {self.exam.subject}"
    
    def __repr__(self):
        return f"<Grade: {self.student.user.username}>"

    @property
    def grade_percent(self):
        return round((self.grade / self.exam.full_score), 2) * 100
    
    def clean(self):
        if self.grade > self.exam.full_score:
            raise ValidationError({"grade": "Grade cannot be higher than full score."}, 
                                  code="invalid_grade")
        super().clean()
        

class Exam(models.Model):
    subject = models.ForeignKey(Subject,
                                on_delete=models.CASCADE,
                                related_name="exam_subject")
    teacher = models.ForeignKey(Teacher,
                                on_delete=models.CASCADE,
                                related_name="exam_teacher")
    exam_class = models.ForeignKey("Class",
                                   related_name="exam_class",
                                   on_delete=models.CASCADE)
    timestamp = models.DateField(db_index=True)
    full_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=20.00,
        blank=True,
    )
    visible_to_students = models.BooleanField(default=True, blank=True)

    @property
    def average_grade(self):
        average_grade = self.grade_exam.all().aggregate(
            average_grade=Avg("grade"))["average_grade"]
        return round(average_grade or 0, 2)

    @property
    def average_grade_percent(self):
        return round(
            (self.average_grade / self.full_score) or 0, 2) * 100
        
    @property
    def school(self):
        return self.exam_class.school.name
    
    def clean(self, *args, **kwargs):
        if self.subject not in self.exam_class.subjects:
            raise ValidationError({"subject": "Subject is not in class."})
        super().clean(*args, **kwargs)

    def __str__(self):
        return f"{self.teacher}, {self.subject}"

    def __repr__(self):
        return f"<Exam: ({self.teacher.user.username}-{self.subject.name})>"

    def get_absolute_url(self):
        return reverse(
            "teachers:exams-detail", kwargs={"pk": self.pk})


class Class(models.Model):
    class_id = models.CharField(max_length=50)
    school = models.ForeignKey(School,
                               related_name="class_school",
                               on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject, 
                                      related_name="class_subjects", 
                                      blank=True)

    def __str__(self):
        return self.class_id
    
    def __repr__(self):
        return f"<Class: {self.class_id}>"

    @property
    def average_grade_percent(self):
        average_percents = [
            exam.average_grade_percent for exam in self.exam_class.all()]
        return round(mean(average_percents or [0]), 2)
    
    def _average_percent_during_a_month(self, date_time):
        filter_month = date_time.month
        filter_year = date_time.year
        exams = self.exam_class.filter(timestamp__month=filter_month,
                                       timestamp__year=filter_year)
        percents = [exam.average_grade_percent for exam in exams]
        return round(mean(percents or [0]))

    def get_grade_percent_eight_months(self):
        percents = []
        init_month = date.today() - relativedelta(months=4)
        for i in range(8):
            month = init_month + relativedelta(months=i)
            percent = self._average_percent_during_a_month(month)
            percents.append(percent)
        return percents

    def get_absolute_url(self):
        return reverse("supports:classes-detail", kwargs={"pk": self.pk})

    class Meta:
        verbose_name_plural = "classes"
        unique_together = ["school", "class_id"]


class Article(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               limit_choices_to=models.Q(user_type="T")
                               | models.Q(user_type="SS"),
                               related_name='article_author',
                               blank=True,
                               null=True)
    school = models.ForeignKey(School,
                               related_name='article_school',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    title = models.CharField(max_length=80)
    categories = ArrayField(base_field=models.CharField(max_length=20), size=5)
    text = RichTextField()
    timestamp = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("home:article-detail", self.pk)
    
    def clean(self, *args, **kwargs):
        if self.user is not None and self.school is not None:
            user_type = self.user.user_type
            match user_type:
                case "SS":
                    school = self.user.school
                    if school is None:
                        raise ValidationError({"school": "School is not set."})
                    if school != self.school:
                        raise ValidationError({"school": "School does not match."})
                case "T":
                    teacher_qs = Teacher.objects.filter(user=self.user)
                    if not teacher_qs.exists():
                        raise ValidationError({"user": "Corresponding teacher does not exist."})
                    school = teacher_qs.first().school
                    if self.school != school:
                        raise ValidationError({"school": "School does not match."})
                case _:
                    raise ValidationError({"user": "User is not a principal or teacher."})
        return super().clean(*args, **kwargs)

    def __str__(self):
        return f"{self.author}: {self.title}"
    
    def __repr__(self):
        return f"<Article: ({self.title}-{self.author.username})>"


class Assignment(models.Model):
    assignment_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="assignment_class",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="assignment_subject",
    )
    body = RichTextField()
    deadline = models.DateField()
    timestamp = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.assignment_class.class_id}-{self.subject.name}"
    
    def __repr__(self):
        return f"<Assignment: \
            ({self.assignment_class.class_id}-{self.subject.name})>"
            
    def reversed(self):
        return self.objects.order_by('-deadline')
            
    def get_absolute_url(self):
        return reverse("home:assignment-detail", kwargs={"pk": self.pk})
    
            
    def clean(self):
        super().clean()
        if not self.subject in self.assignment_class.subjects.all():
            raise ValidationError({"subject": "Subject must be in class."},
                                  code="invalid_subject")
