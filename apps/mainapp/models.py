from django.db import models
from django.db.models import Avg, Q
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from datetime import date
from statistics import mean
from typing import List
from decimal import Decimal
from functools import partial
from operator import is_not

from .managers import *
from .helpers import loop_through_month_number


class School(models.Model):
    name = models.CharField(max_length=100)
    support = models.OneToOneField(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="school_support",
        limit_choices_to={"user_type": "SS"},
    )

    class Meta:
        unique_together = ["name", "support"]
        permissions = (("support", "has support staff's permissions"), )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        permission = Permission.objects.get(codename="support")
        self.support.user_permissions.add(permission)


class Teacher(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    school = models.ForeignKey("School",
                               on_delete=models.CASCADE,
                               related_name="teacher_school")
    degree = models.CharField(max_length=100, blank=True)
    university = models.CharField(max_length=100, blank=True)

    class Meta:
        permissions = (("teacher", "has teachers' permissions"), )

    def __str__(self):
        return (self.user.first_name + " " + self.user.last_name).title()

    def get_absolute_url(self):
        return reverse("support:teachers-detail", kwargs={"pk": self.pk})

    def get_performance_percent_six_months(self):
        percents = []
        init_month = date.today().month - 3
        for i in range(6):
            year = loop_through_month_number(init_month + i)[0]
            month = loop_through_month_number(init_month + i)[1]
            exams = self.exam_teacher.filter(
                Q(timestamp__year=year) & Q(timestamp__month=month))
            if exams.count() >= 1:
                average_grade_uncleaned = [
                    *map(lambda exam: float(exam.get_average_grade_percent()),
                         exams)
                ]
                average_grade_cleaned = filter(partial(is_not, None),
                                               average_grade_uncleaned)
                average_grade = mean([*average_grade_cleaned] or [0])
            else:
                average_grade = 0
            percents.append(average_grade)
        return percents

    def get_average_performance_six_months(self) -> Decimal:
        """Returns a decimal representing the overall average performance."""
        return round(mean(self.get_performance_percent_six_months() or [0]), 2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.user.user_type != "T":
            raise ValidationError("User must be typed as a teacher.")
        group, group_created = Group.objects.get_or_create(name="Teachers")
        if group_created:
            perm = Permission.objects.get(codename="teacher")
            group.permissions.add(perm)
        self.user.groups.add(group)


class Student(models.Model):
    user = models.OneToOneField(get_user_model(),
                                related_name="student_user",
                                on_delete=models.CASCADE)
    student_class = models.ForeignKey(
        "Class",
        on_delete=models.SET_NULL,
        null=True,
        related_name="student_class",
        blank=True)

    def __str__(self):
        return self.user.user_id

    def get_absolute_url_supports(self):
        return reverse("support:students-detail", kwargs={"pk": self.pk})

    def get_absolute_url_teachers(self):
        return reverse("teachers:students-detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.user.user_type != "S":
            raise ValidationError("User must be typed as a student.")


class Subject(models.Model):
    name = models.CharField(max_length=30)
    teacher = models.ForeignKey(Teacher,
                                on_delete=models.CASCADE,
                                related_name="subject_teacher")

    def __str__(self):
        return f"{self.name} - {self.teacher}"

    def get_absolute_url(self):
        return reverse("support:subjects-detail", kwargs={"pk": self.pk})

    class Meta:
        unique_together = ["name", "teacher"]


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

    def get_grade_percent(self) -> Decimal:
        """
        Returns the percentage grade.
        """
        return round((self.grade / self.exam.full_score) * 100, 2)

    def save(self, *args, **kwargs) -> None:
        if self.grade > self.exam.full_score:
            raise ValidationError("The grade exceeds the full score",
                                  code="invalid_grade")
        else:
            super().save(*args, **kwargs)


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
    timestamp = models.DateField()
    full_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=20,
    )

    def get_average_grade(self):
        """
        Returns the average grade achieved.
        """
        average_grade = self.grade_exam.all().aggregate(
            average_grade=Avg("grade"))["average_grade"]
        return round(average_grade or 0, 2)

    def get_average_grade_percent(self):
        """
        Returns average percentage grade achieved.
        """
        return round((self.get_average_grade() / self.full_score) * 100 or 0,
                     2)

    def __str__(self):
        return f"{self.teacher}, {self.subject}"

    def get_absolute_url(self):
        return reverse("teachers:exams-detail", kwargs={"pk": self.pk})


class Class(models.Model):
    class_id = models.CharField(max_length=50)
    school = models.ForeignKey(School,
                               related_name="class_school",
                               on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject, related_name="class_subjects")

    def __str__(self):
        return self.class_id

    def get_average_grade_percent(self) -> Decimal:
        """
        Return average percentage grade achieved by the students of a class.
        """
        average_percents = []
        for exam in self.exam_class.all():
            exam_average_grade = exam.get_average_grade_percent()
            average_percents.append(exam_average_grade or 0)
        return round(mean(average_percents or [0]), 2)

    def get_average_percent_within_a_month(self, filter_params_list):
        percents = []
        filter_month = filter_params_list[1]
        filter_year = filter_params_list[0]
        exams = self.exam_class.filter(timestamp__month=filter_month,
                                       timestamp__year=filter_year)
        for exam in exams:
            exam_average_grade = exam.get_average_grade_percent()
            percents.append(exam_average_grade)
        return round(mean(percents or [0]))

    def get_performance_percent_eight_months(self):
        percents = []
        init_month = date.today().month - 4
        for i in range(0, 8):
            month = loop_through_month_number(init_month + i)
            percent = self.get_average_percent_within_a_month(month)
            percents.append(percent)
        return percents

    def get_absolute_url(self):
        return reverse("support:classes-detail", kwargs={"pk": self.pk})

    class Meta:
        verbose_name_plural = "classes"
        unique_together = ["school", "class_id"]
