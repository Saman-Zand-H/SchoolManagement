from django.urls import path

from . import views

app_name = "teachers"

urlpatterns = [
    path("", views.dashboard_view, name="home"),
    path("exams/", views.exams_list_view, name="exams"),
    path("ajax/exams/create/", views.ajax_create_exam, name="ajax-add-exam"),
    path("exams/detail/<int:pk>/", views.exam_detail_view, name="exams-detail"),
    path("students/", views.students_view, name="students"),
    path("students/<int:pk>",
         views.students_detail_view,
         name="students-detail"),
    path("classes/", views.classes_view, name="classes"),
]
