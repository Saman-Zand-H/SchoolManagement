# from django.db import models
# from django.db.models import Avg
# from django.urls import reverse
# from django.contrib.auth import get_user_model
# from django.contrib.auth.models import Permission, Group
# from django.contrib.contenttypes.models import ContentType
# from django.core.exceptions import ValidationError

# from mainapp.helpers import loop_through_month_number

# from datetime import date

# from mainapp.models import *


# class Teacher(models.Model):
#     user = models.OneToOneField(
#         get_user_model(),
#         on_delete=models.CASCADE,
#     )
#     # TODO: Set null and blank to false
#     degree = models.CharField(blank=True, null=True, max_length=20, default="")
#     university = models.CharField(
#         blank=True, null=True, max_length=20, default="")

#     def __str__(self):
#         return self.user.user_id

#     def get_performance_percent_six_months(self):
#         percents = []
#         init_month = date.today().month - 3
#         for teacher_class in self.class_teachers.all():
#             for i in range(0, 6):
#                 month = loop_through_month_number(init_month + i)
#                 percent = teacher_class.get_average_percent_within_a_month(
#                     month)
#                 percents.append(percent)
#         return percents

#     def save(self, *args, **kwargs):
#         save = super().save(*args, **kwargs)
#         content_type = ContentType.objects.get_for_model(Teacher)
#         group, group_created = Group.objects.get_or_create(name="teachers")
#         if group_created:
#             perm, perm_created = Permission.objects.get_or_create(
#                 codename="teacher_permission",
#                 name="has teacher permissions",
#                 content_type=content_type,
#             )
#             group.permissions.add(perm)
#         self.user.groups.add(group)
#         return save


# class Grade(models.Model):
#     student = models.ForeignKey(
#         "Student",
#         on_delete=models.CASCADE,
#         related_name="grade_user",
#     )
#     subject = models.ForeignKey(
#         Subject,
#         on_delete=models.CASCADE,
#         related_name="grade_subject",
#     )
#     grade = models.DecimalField(
#         max_digits=6,
#         decimal_places=2,
#         default=0.00,
#         null=True,
#         blank=True,
#     )
#     exam = models.ForeignKey(
#         "Exam",
#         related_name="grade_exam",
#         on_delete=models.CASCADE,
#     )

#     def __str__(self):
#         return f"{self.student}, {self.subject}"

#     def get_grade_percent(self):
#         return round((self.grade / self.exam.full_score) * 100, 2)

#     def save(self, *args, **kwargs):
#         if self.grade > self.exam.full_score:
#             raise ValidationError("grade value is greater than fullscore")
#         else:
#             super(Grade, self).save(*args, **kwargs)


# class Exam(models.Model):
#     subject = models.ForeignKey(
#         Subject,
#         on_delete=models.CASCADE,
#         related_name="exam_subject"
#     )
#     teacher = models.ForeignKey(
#         Teacher,
#         on_delete=models.CASCADE,
#         related_name="exam_subject",
#     )
#     exam_class = models.ForeignKey(
#         Class,
#         related_name="exam_class",
#         on_delete=models.CASCADE,
#     )
#     timestamp = models.DateField()
#     grades = models.ManyToManyField(
#         Grade,
#         related_name="exam_grades",
#         blank=True,
#     )
#     full_score = models.DecimalField(max_digits=6, decimal_places=2)

#     def get_average_grade(self):
#         average_grade = self.grades.all().aggregate(
#             average_grade=Avg("grade"))["average_grade"]
#         return round(average_grade or 0, 2)

#     def get_average_grade_percent(self):
#         return round((self.get_average_grade() / self.full_score) * 100 or 0, 2)

#     def __str__(self):
#         return f"{self.teacher}, {self.subject}"

#     def get_absolute_url(self):
#         return reverse("teachers:exams-detail", kwargs={"pk": self.pk})
