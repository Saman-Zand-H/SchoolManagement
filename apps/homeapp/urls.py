from django.urls import path

from . import views

app_name = "home"

urlpatterns = [
    path("", views.homepageview, name="home"),
    path("support-page/", views.support_view, name="support-page"),
    path("set-language/", views.set_language, name="set_language")
]
