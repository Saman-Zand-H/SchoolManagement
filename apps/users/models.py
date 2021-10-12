from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


USER_TYPE_CHOICES = (
    ("S", "student"),
    ("T", "teacher"),
    ("IT", "IT staff"),
    ("P", "principal"),
    ("O", "others"),
)


class CustomManager(BaseUserManager):
    def _create_user(self, user_id, email, first_name, last_name, password, 
                    user_type, image, is_superuser, is_staff, **extra_fields):
        now = timezone.now()
        user_email = self.normalize_email(email)
        user = self.model(
            user_id=user_id,
            email=user_email,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            image=image,
            is_superuser=is_superuser,
            is_staff=is_staff,
            last_login=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, user_id=None, email=None, first_name=None, last_name=None,
                    password=None, user_type=None, image=None, **extra_fields):
        return self._create_user(user_id, email, first_name, last_name, password, user_type, image, False, False)

    def create_staff(self, user_id=None, email=None, first_name=None, last_name=None,
                    password=None, user_type=None, image=None, **extra_fields):
        return self._create_user(user_id, email, first_name, last_name, password, user_type, image, False, True)

    def create_superuser(self, user_id=None, email=None, first_name=None, last_name=None,
                        password=None, user_type=None, image=None, **extra_fields):
        user = self._create_user(
            user_id, email, first_name, last_name,password, user_type, image, True, True)
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField(
        max_length=254, unique=True, blank=True, null=True)
    # TODO: Set null to False
    first_name = models.CharField(max_length=254, blank=True, null=True)
    last_name = models.CharField(max_length=254, blank=True, default="j")
    phone_number = PhoneNumberField(blank=True, null=True)
    user_type = models.CharField(max_length=3, choices=USER_TYPE_CHOICES, null=True)
    picture = models.ImageField(
        null=True, blank=True, upload_to="media", default="empty-profile.jpg")
    about = models.TextField(null=True, blank=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'user_id'
    EMAIL_FIELD = 'email'

    REQUIRED_FIELDS = []

    objects = CustomManager()

    def get_absolute_url(self):
        return f"/users/{self.pk}/"

    def get_user_id(self):
        return self.user_id

    def name(self):
        return self.first_name + " " + self.last_name

    def __str__(self):
        return self.get_user_id()
