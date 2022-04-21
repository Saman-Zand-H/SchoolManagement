from django.urls import path

from . import views


app_name = "students"


urlpatterns = [
    path("", views.dashboard_view, name="home"),
    path("grades/", views.exams_view, name="exams"),
]