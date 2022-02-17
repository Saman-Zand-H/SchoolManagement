from django.contrib import admin

from .models import *


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    pass


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = [
        "teacher",
        "exam_class",
        "subject",
        "timestamp",
    ]


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ["student", "grade", "exam"]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["user", "student_class"]
