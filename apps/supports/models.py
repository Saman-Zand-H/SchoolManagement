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
            ("api_post", "has permission to send a post_request to api"),
        )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        group, group_created = Group.objects.get_or_create(name="Principals")
        if group_created:
            support_perm = Permission.objects.filter(codename="support")[0]
            api_perm = Permission.objects.filter(codename="api_post")[0]
            group.permissions.add(support_perm)
            group.permissions.add(api_perm)
        self.support.groups.add(group)
        super().save(*args, **kwargs)
