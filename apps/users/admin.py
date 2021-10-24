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
                "phone_number",
                "picture",
                "password1",
                "password2",
            ),
            "classes":
            "wide",
        },
    ), )
    list_display = ["user_id", "first_name", "user_type"]
    search_fields = ["user_id", "first_name"]
    list_filter = ["user_type"]
    filter_horizontal = ["groups", "user_permissions"]
