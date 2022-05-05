from django import template
from django.db.models import Q

from datetime import date, timedelta

from mainapp.models import Exam


register = template.Library()

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
    return getbyindex(queryset, pk).user.name

@register.filter
def set_average_grade_color(percent):
    if percent < 40:
        return "danger"
    elif 40 < percent < 70:
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
    
@register.filter
def get_group_name(chatgroup, user):
    return chatgroup.get_name(user)

@register.filter
def get_group_photo(chatgroup, user):
    return chatgroup.get_picture(user)
