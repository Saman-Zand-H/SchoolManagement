from django.contrib import admin

from .models import *

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    pass

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    pass

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    pass

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    pass

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    pass

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    pass