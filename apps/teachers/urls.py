from django.urls import path

from . import views


app_name = "teachers"

urlpatterns = [
    path("", views.dashboardview, name="dashboard"),
    path("exams/", views.examslistview, name="exams"),
    path("exams/create/", views.createexamview, name="add-exam"),
    path("exams/<int:pk>/", views.setgradesview, name="exams-detail"),
    path("exams/<int:pk>/del/", views.deleteexamview, name="del-exam"),
    path("classes/", views.classesview, name="class"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
]
