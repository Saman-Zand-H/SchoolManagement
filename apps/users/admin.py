from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, PhoneNumber


@admin.register(CustomUser)
class CustomAdmin(UserAdmin):
    ordering = ["user_id"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user_id",
                    "user_type",
                    "email",
                    "first_name",
                    "last_name",
                    "picture",
                    "about",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = ((
        None,
        {
            "fields": (
                "user_id",
                "user_type",
                "email",
                "first_name",
                "last_name",
                "picture",
                "password1",
                "password2",
                "about",
            ),
            "classes":
            "wide",
        },
    ), )
    list_display = ["name", "user_id", "user_type", "email"]
    search_fields = ["name", "user_id", "email"]
    list_filter = ["user_type"]
    filter_horizontal = ["groups", "user_permissions"]


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ["user", "phonenumber", "verified"]
    search_fields = ["user", "phonenumber"]
