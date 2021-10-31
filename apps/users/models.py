from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.utils import timezone
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError

import logging

logger = logging.getLogger(__name__)

USER_TYPE_CHOICES = (
    ("S", "student"),
    ("T", "teacher"),
    ("SS", "support staff"),
    ("P", "principal"),
)


def validate_file_extension(file):
    import os

    ext = os.path.splitext(file.name)[1]
    valid_exts = [".jpg", ".png"]
    if not ext.lower() in valid_exts:
        logger.error(f"Unsupported file detected for: {file.name}.")
        raise ValidationError("Invalid file extension.")


def validate_file_size(file):
    if file.size > 3 * 1024 * 1024:
        logger.error(f"Maximum image file size exceeded for: {file.name}")
        raise ValidationError("Unacceptable file size.")


class CustomManager(BaseUserManager):
    def _create_user(
        self,
        user_id,
        first_name,
        last_name,
        password,
        user_type,
        picture,
        is_superuser,
        is_staff,
        **extra_fields,
    ):
        now = timezone.now()
        user = self.model(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            picture=picture,
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
        user_id=None,
        first_name=None,
        last_name=None,
        password=None,
        user_type=None,
        picture=None,
        **extra_fields,
    ):
        return self._create_user(user_id, first_name, last_name, password,
                                 user_type, picture, False, False,
                                 **extra_fields)

    def create_staff(
        self,
        user_id=None,
        first_name=None,
        last_name=None,
        password=None,
        user_type=None,
        picture=None,
        **extra_fields,
    ):
        return self._create_user(user_id, first_name, last_name, password,
                                 user_type, picture, False, True,
                                 **extra_fields)

    def create_superuser(
        self,
        user_id=None,
        first_name=None,
        last_name=None,
        password=None,
        user_type=None,
        picture=None,
        **extra_fields,
    ):
        user = self._create_user(user_id, first_name, last_name, password,
                                 user_type, picture, True, True,
                                 **extra_fields)
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=254)
    last_name = models.CharField(max_length=254)
    phone_number = PhoneNumberField(blank=True, null=True)
    user_type = models.CharField(max_length=3, choices=USER_TYPE_CHOICES)
    picture = models.FileField(blank=True,
                               upload_to="media",
                               default="empty-profile.jpg",
                               validators=[validate_file_extension, validate_file_size])
    about = models.TextField(blank=True, default="")
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "user_id"
    EMAIL_FIELD = ""
    REQUIRED_FIELDS = ["user_type", "first_name", "last_name"]

    objects = CustomManager()

    def get_absolute_url(self):
        return f"/users/{self.pk}/"

    def name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.user_id
