from django.urls import path

from . import views


app_name = "students"


urlpatterns = [
    path("", views.dashboard_view, name="home"),
]