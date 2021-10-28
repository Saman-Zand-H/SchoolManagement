from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


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
                    "first_name",
                    "last_name",
                    "phone_number",
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
                "first_name",
                "last_name",
                "phone_number",
                "picture",
                "password1",
                "password2",
                "about",
            ),
            "classes":
            "wide",
        },
    ), )
    list_display = ["name", "user_id", "user_type"]
    search_fields = ["name", "user_id"]
    list_filter = ["user_type"]
    filter_horizontal = ["groups", "user_permissions"]
