from django.urls import path

from . import views

app_name = "support"
urlpatterns = [
    path("account/signup/school",
         views.createschool_view,
         name="create-school"),
    path("", views.HomeView.as_view(), name="home"),
    path("classes/", views.classes_view, name="classes"),
    path("classes/<int:pk>/", views.classes_detailview, name="classes-detail"),
    path("students/", views.students_view, name="students"),
    path("students/<int:pk>", views.students_detailview, name="students-detail"),
    path("teachers/", views.teachers_view, name="teachers"),
    path("teachers/<int:pk>/",
         views.teachers_detailview,
         name="teachers-detail"),
    path("subjects/", views.subjects_view, name="subjects"),
    path("subjects/<int:pk>/", views.subjects_detailview, name="subjects-detail"),
]
