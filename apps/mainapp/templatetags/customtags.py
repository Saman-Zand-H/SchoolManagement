from django import template
from django.db.models import Q, Count

from datetime import date, timedelta

from mainapp.models import Student, Exam


register = template.Library()

@register.filter
def get_pk(pk):
    return pk - 1

@register.filter(name="getbyindex")
def getbyindex(item, index:int):
    return item[index - 1]

@register.filter
def return_student(queryset, pk):
    return queryset.get(pk=pk).user.name

@register.filter
def return_student_pk(queryset, pk):
    return getbyindex(queryset, pk).pk

@register.filter
def getuserbyindex(queryset, pk):
    return getbyindex(queryset, pk).user.name()

@register.filter
def integerify(obj, index):
    return int(index)

@register.filter
def set_average_grade_color(percent):
    if percent < 40:
        return "danger"
    elif 40< percent < 70:
        return "warning"
    else:
        return "success"

@register.filter
def get_students_class_header(queryset):
    return queryset.student_class.all()[:3]

@register.filter
def get_last_week_exams_difference(teacher):
    today = date.today()
    week_timedelta = timedelta(weeks=1)
    exams = Exam.objects.filter(Q(teacher=teacher) & Q(timestamp__gt=today-week_timedelta))
    return exams.count() or 0

@register.filter
def get_teacher_students_count(class_queryset):
    return Student.objects.filter(student_class__in=class_queryset).count()

@register.filter
def dir_s(obj):
    return dir(obj) 