from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_noop as _

from datetime import date
from dateutil.relativedelta import relativedelta
from operator import is_not
from functools import partial
from statistics import mean
from logging import getLogger

from supports.models import School

logger = getLogger(__name__)


class Teacher(models.Model):
    user = models.OneToOneField(get_user_model(),
                                on_delete=models.CASCADE,
                                limit_choices_to={"user_type": "T"},
                                related_name="teacher_user")
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

    @property
    def percents_six_months(self):
        percents = []
        init_month = date.today() - relativedelta(months=3)
        for i in range(6):
            timestamp = init_month + relativedelta(months=i)
            exams = self.exam_teacher.filter(
                Q(timestamp__year=timestamp.year) & Q(timestamp__month=timestamp.month))
            if exams.exists():
                average_percents = [float(exam.average_grade_percent) for exam in exams]
                average_percent = round(mean(average_percents), 2)
            else:
                average_percent = None
            percents.append(average_percent)
        return percents

    @property
    def average_percent_six_months(self):
        if self.percents_six_months is not None:
            return round(mean(
                [*filter(partial(is_not, None), self.percents_six_months)]), 2)
        return 0
    
    def clean(self):
        super().clean()
        if self.user.user_type != "T":
            logger.error(
                _("A non-teacher typed user was being used as a teacher."))
            raise ValidationError(
                _("{} is not a teacher. User must be typed as a teacher.").
                format(self.user.name))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        group, group_created = Group.objects.get_or_create(name="Teachers")
        if group_created:
            perm = Permission.objects.filter(codename="teacher")[0]
            group.permissions.add(perm)
        self.user.groups.add(group)
