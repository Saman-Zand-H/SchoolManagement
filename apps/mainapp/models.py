from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models import Avg
from django.core.exceptions import ValidationError
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_noop
from django.utils.translation import gettext_lazy as _
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
                                      verbose_name=_("Student Class"),
                                      blank=True)

    def __str__(self):
        return self.user.username

    def get_absolute_url_supports(self):
        return reverse("supports:students-detail", kwargs={"pk": self.pk})

    def get_absolute_url_teachers(self):
        return reverse("teachers:students-detail", kwargs={"pk": self.pk})
    
    def clean(self):
        super().clean()
        if self.user.user_type != "S":
            logger.error(
                gettext_noop(
                    "A non-student typed user was being used as a student."))
            raise ValidationError(
                gettext_noop(
                    "{} is not a student. User must be typed as a student.").
                format(self.user.name))


class Subject(models.Model):
    name = models.CharField(max_length=30)
    teacher = models.ForeignKey(Teacher,
                                on_delete=models.CASCADE,
                                related_name="subject_teacher")

    def __str__(self):
        return f"{self.name} - {self.teacher}"

    def get_absolute_url(self):
        return reverse("supports:subjects-detail", kwargs={"pk": self.pk})

    class Meta:
        unique_together = ["name", "teacher"]
        verbose_name = _("Courses")
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

    @property
    def grade_percent(self):
        return round((self.grade / self.exam.full_score), 2) * 100
    
    def clean(self):
        if self.grade > self.exam.full_score:
            raise ValidationError({"grade": _("Grade cannot be higher than full score.")}, 
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
        default=20,
    )

    @property
    def average_grade(self):
        average_grade = self.grade_exam.all().aggregate(
            average_grade=Avg("grade"))["average_grade"]
        return round(average_grade or 0, 2)

    @property
    def average_grade_percent(self):
        return round(
            (self.average_grade / self.full_score) or 0, 2) * 100

    def __str__(self):
        return f"{self.teacher}, {self.subject}"

    def get_absolute_url(self):
        return reverse(
            "teachers:exams-detail", kwargs={"pk": self.pk})


class Class(models.Model):
    class_id = models.CharField(max_length=50)
    school = models.ForeignKey(School,
                               related_name="class_school",
                               on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject, related_name="class_subjects")

    def __str__(self):
        return self.class_id

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

    def __str__(self):
        return f"{self.author}: {self.title}"
