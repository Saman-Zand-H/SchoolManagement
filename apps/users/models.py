from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from algoliasearch_django import get_adapter

import logging

logger = logging.getLogger(__name__)

USER_TYPE_CHOICES = (
    ("S", "student"),
    ("T", "teacher"),
    ("SS", "support staff"),
)


def validate_file_extension(file):
    import os

    ext = os.path.splitext(file.name)[1]
    valid_extensions = [".jpg", ".png"]
    if not ext.lower() in valid_extensions:
        logger.error("Unsupported file detected by: {}.".format(file.name))
        raise ValidationError("Invalid file extension.")


def validate_file_size(file):
    if file.size > 3 * 1024 * 1024:
        logger.error(
            "Maximum image file size exceeded by: {}.".format(file.name))
        raise ValidationError("Unacceptable file size.")


class CustomManager(BaseUserManager):
    def _create_user(
        self,
        username,
        email,
        first_name,
        last_name,
        password,
        user_type,
        picture,
        is_active,
        is_superuser,
        is_staff,
        **extra_fields,
    ):
        now = timezone.now()
        user_email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=user_email,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            picture=picture,
            is_active=is_active,
            is_superuser=is_superuser,
            is_staff=is_staff,
            last_login=now,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        username=None,
        email=None,
        first_name=None,
        last_name=None,
        password=None,
        user_type=None,
        picture=None,
        **extra_fields,
    ):
        return self._create_user(username, email, first_name, last_name,
                                 password, user_type, picture, True, False,
                                 False, **extra_fields)

    def create_staff(
        self,
        username=None,
        email=None,
        first_name=None,
        last_name=None,
        password=None,
        user_type=None,
        picture=None,
        **extra_fields,
    ):
        return self._create_user(username, email, first_name, last_name,
                                 password, user_type, picture, True, False,
                                 True, **extra_fields)

    def create_superuser(
        self,
        username=None,
        email=None,
        first_name=None,
        last_name=None,
        password=None,
        user_type=None,
        picture=None,
        **extra_fields,
    ):
        user = self._create_user(username, email, first_name, last_name,
                                 password, user_type, picture, True, True,
                                 True, **extra_fields)
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=254)
    last_name = models.CharField(max_length=254)
    user_type = models.CharField(max_length=3, choices=USER_TYPE_CHOICES)
    picture = models.ImageField(
        blank=True,
        null=True,
        upload_to="media",
        validators=[validate_file_size])
    about = models.TextField(blank=True, null=True)
    is_superuser = models.BooleanField(default=False, blank=True)
    is_staff = models.BooleanField(default=False, blank=True)
    is_active = models.BooleanField(default=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["user_type", "first_name", "last_name"]

    objects = CustomManager()
    
    class Meta:
        verbose_name = "User Model"
        verbose_name_plural = "User Model"

    def get_absolute_url(self):
        return f"/users/{self.pk}/"

    @property
    def name(self):
        return f"{self.first_name.title()} {self.last_name.title()}".strip()
    
    @classmethod
    def get_index_name(cls):
        return getattr(get_adapter(cls), "index_name")

    def __str__(self):
        return self.username
    
    def is_not_principal(self):
        return self.user_type != "SS"
    
    def get_dashboard_url(self):
        match self.user_type:
            case "T":
                return reverse("teachers:home")
            case "SS":
                return reverse("supports:home")
            case "S":
                return reverse("students:home")
    
    @property
    def owned_groups(self):
        return self.chatgroup_owner.all()
    
    @property
    def get_picture_url(self):
        return self.picture.url if self.picture else static(
            "assets/img/icons/empty-profile.jpg")
    
    @property
    def school(self):
        if hasattr(self, "school_support"):
            return self.school_support
        elif hasattr(self, "student_user"):
            return self.student_user.student_class.school
        elif hasattr(self, "teacher_user"):
            return self.teacher_user.school
    
    @property
    def school_name_tag(self):
        # Don't ask why I used this dummy format here. Instead,
        # ask Algolia why they used a list() instead of a [* ]
        if hasattr(self.school, "name"):
            return [self.school.name]
        return [""]

    def save(self, *args, **kwargs):
        if not self.email:
            self.email = None
        super().save(*args, **kwargs)
