from django.contrib import admin

from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "school",
        "university",
    ]
    search_fields = [
        "user",
        "school"
    ]
