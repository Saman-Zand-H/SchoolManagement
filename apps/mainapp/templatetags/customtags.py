from django import template

from datetime import datetime


register = template.Library()

@register.filter
def get_pk(pk):
    return pk - 1

@register.filter(name="getbyindex")
def getbyindex(item, index:int):
    return item[index - 1]

@register.filter
def return_student(queryset, pk):
    return queryset.get(pk=pk).user.user_id

@register.filter
def return_student_pk(queryset, pk):
    return getbyindex(queryset, pk).pk

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