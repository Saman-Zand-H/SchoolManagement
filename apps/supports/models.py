from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group


class School(models.Model):
    name = models.CharField(max_length=100)
    support = models.OneToOneField(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="school_support",
        limit_choices_to={"user_type": "SS"},
    )

    class Meta:
        unique_together = ["name", "support"]
        permissions = (
            ("support", "has support staff's permissions"), 
        )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        group, group_created = Group.objects.get_or_create(name="Principals")
        if group_created:
            perm = Permission.objects.filter(codename="support")[0]
            group.permissions.add(perm)
        self.support.groups.add(group)
        super().save(*args, **kwargs)
