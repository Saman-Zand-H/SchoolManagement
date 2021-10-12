from django.db import models
from django.db.models import Manager, Avg
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from datetime import date
from statistics import mean

from .managers import *
from .helpers import loop_through_month_number


class Teacher(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    classes = models.ManyToManyField(
        'Class', 
        related_name="teacher_classes",
        blank=True,
    )
    # TODO: Set null and blank to false
    degree = models.CharField(blank=True, null=True, max_length=20, default="")
    university = models.CharField(blank=True, null=True, max_length=20, default="")

    def __str__(self):
        return self.user.user_id

    def get_performance_percent_six_months(self):
        percents = []
        init_month = date.today().month - 3
        for teacher_class in self.class_teachers.all():
            for i in range(0, 6):
                month = loop_through_month_number(init_month + i)
                percent = teacher_class.get_average_percent_within_a_month(month)
                percents.append(percent)
        return percents
    
    def save(self, *args, **kwargs):
        save = super().save(*args, **kwargs)
        content_type = ContentType.objects.get_for_model(Teacher)
        group, group_created = Group.objects.get_or_create(name="teachers")
        if group_created:
            perm, perm_created = Permission.objects.get_or_create(
                codename="teacher_permission", 
                name="has teacher permissions",
                content_type=content_type,
            )
            group.permissions.add(perm)
        self.user.groups.add(group)
        return save


class Student(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    exams = models.ManyToManyField(
        "Exam",
        related_name="student_exams",
        blank=True,
    )

    objects = Manager()
    student_class = StudentClass()
    all_grades = StudentManager()

    def __str__(self):
        return self.user.user_id


class Subject(models.Model):
    name = models.CharField(max_length=30)
    teachers = models.ManyToManyField(
        Teacher, 
        related_name="subject_teacher",
        blank=True,
    )

    objects = Manager()
    all_teachers = SubjectTeachers()

    def __str__(self):
        return self.name


class Grade(models.Model):
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name="grade_user",
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        related_name="grade_subject",
    )
    grade = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        validators=[],
        default=0.00, 
        null=True, 
        blank=True,
    )
    exam = models.ForeignKey(
        "Exam",
        related_name="grade_exam",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.student}, {self.subject}"

    def get_grade_percent(self):
        return round((self.grade / self.exam.full_score) * 100, 2)

    def save(self, *args, **kwargs):
        if self.grade > self.exam.full_score:
            raise ValidationError("grade value is greater than fullscore")
        else:
            super(Grade, self).save(*args, **kwargs)


class Exam(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="exam_subject"
    )
    teacher = models.ForeignKey(
        Teacher, 
        on_delete=models.CASCADE, 
        related_name="exam_subject",
    )
    exam_class = models.ForeignKey(
        "Class",
        related_name="exam_class",
        on_delete=models.CASCADE,
    )
    timestamp = models.DateField()
    grades = models.ManyToManyField(
        Grade, 
        related_name="exam_grades",
        blank=True,
    )
    full_score = models.DecimalField(max_digits=6, decimal_places=2)

    def get_average_grade(self):
        average_grade = self.grades.all().aggregate(
            average_grade=Avg("grade"))["average_grade"]
        return round(average_grade or 0, 2)

    def get_average_grade_percent(self):
        return round((self.get_average_grade() / self.full_score) * 100 or 0, 2)

    def __str__(self):
        return f"{self.teacher}, {self.subject}"

    def get_absolute_url(self):
        return reverse("teachers:exams-detail", kwargs={"pk": self.pk})


class Class(models.Model):
    class_id = models.CharField(max_length=5)
    subjects = models.ManyToManyField(
        Subject,
        related_name="class_subjects",
        blank=True,
    )
    exams = models.ManyToManyField(
        Exam, 
        related_name="class_exams",
        blank=True,
    )
    students = models.ManyToManyField(
        Student, 
        related_name="class_students",
        blank=True,
    )
    teachers = models.ManyToManyField(
        Teacher, 
        related_name="class_teachers",
        blank=True,
    )

    objects = Manager()
    all_teachers = ClassTeachers()
    all_students = ClassStudents()

    def __str__(self):
        return self.class_id

    def get_average_grade(self):
        average_grades = []
        for exam in self.exams.all():
            average_grades.append(exam.get_average_grade())
        return round(mean(average_grades or [0]), 2)

    def get_average_grade_percent(self):
        average_percents = []
        for exam in self.exams.all():
            average_percents.append(exam.get_average_grade_percent())
        return round(mean(average_percents) or [0], 2)

    def get_average_percent_within_a_month(self, filter_params_list):
        percents = []
        filter_month = filter_params_list[0]
        filter_year = filter_params_list[1]
        queryset = self.exams.filter(timestamp__month=filter_month, timestamp__year=filter_year)
        for query in queryset:
            percents.append(query.get_average_grade_percent())
        return round(mean(percents or [0]))
    
    def get_performance_percent_eight_months(self):
        percents = []
        init_month = date.today().month - 4
        for i in range(0, 8):
            month = loop_through_month_number(init_month + i)
            percent = self.get_average_percent_within_a_month(month)
            percents.append(percent)
        return percents

    class Meta:
        verbose_name_plural = "classes"
