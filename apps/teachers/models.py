from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_noop as _

from datetime import date
from functools import partial
from operator import is_not
from decimal import Decimal
from statistics import mean
from logging import getLogger

from mainapp.helpers import loop_through_month_number
from supports.models import School

logger = getLogger(__name__)


class Teacher(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    school = models.ForeignKey(School,
                               on_delete=models.CASCADE,
                               related_name="teacher_school")
    degree = models.CharField(max_length=100, blank=True)
    university = models.CharField(max_length=100, blank=True)

    class Meta:
        permissions = (("teacher", "has teachers' permissions"), )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def get_absolute_url(self):
        return reverse("supports:teachers-detail", kwargs={"pk": self.pk})

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
                average_grade = round(mean([*average_grade_cleaned] or [0]), 2)
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
            logger.error(
                _("A non-teacher typed user was being used as a teacher."))
            raise ValidationError(
                _("{} is not a teacher. User must be typed as a teacher.").
                format(self.user.name))
        group, group_created = Group.objects.get_or_create(name="Teachers")
        if group_created:
            perm = Permission.objects.filter(codename="teacher")[0]
            group.permissions.add(perm)
        self.user.groups.add(group)
