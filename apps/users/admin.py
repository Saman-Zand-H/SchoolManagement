from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomAdmin(UserAdmin):
    ordering = ["username"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
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
                "username",
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
    list_display = ["name", "username", "user_type", "email"]
    search_fields = ["name", "username", "email"]
    list_filter = ["user_type"]
    filter_horizontal = ["groups", "user_permissions"]
