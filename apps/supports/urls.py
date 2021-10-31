from django.urls import path

from . import views

app_name = "support"
urlpatterns = [
    path("account/signup/school/",
         views.createschool_view,
         name="create-school"),
    path("", views.home_view, name="home"),
    path("classes/", views.classes_view, name="classes"),
    path("classes/<int:pk>/", views.classes_detailview, name="classes-detail"),
    path("classes/<int:pk>/del/", views.deleteclass_view, name="classes-del"),
    path("students/", views.students_view, name="students"),
    path("students/<int:pk>/",
         views.students_detailview,
         name="students-detail"),
    path("students/<int:pk>/del/",
         views.deletestudent_view,
         name="students-del"),
    path("teachers/", views.teachers_view, name="teachers"),
    path("teachers/<int:pk>/",
         views.teachers_detailview,
         name="teachers-detail"),
    path("teachers/<int:pk>/del/",
         views.deleteteacher_view,
         name="teachers-del"),
    path("subjects/", views.subjects_view, name="subjects"),
    path("subjects/<int:pk>/",
         views.subjects_detailview,
         name="subjects-detail"),
    path("subjects/<int:pk>/del/",
         views.deletesubject_view,
         name="subjects-del"),
]
