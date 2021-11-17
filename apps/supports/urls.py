from django.urls import path

from . import views

app_name = "support"
urlpatterns = [
    # TODO: PLEASE MOVE THIS PIECE OF SHIT TO USERS APP ASAP
    path("account/signup/school/",
         views.create_school_view,
         name="create-school"),
    path("", views.home_view, name="home"),
    path("classes/", views.classes_view, name="classes"),
    path("classes/<int:pk>/", views.classes_detail_view,
         name="classes-detail"),
    path("classes/<int:pk>/del/", views.delete_class_view, name="classes-del"),
    path("students/", views.students_view, name="students"),
    path("students/<int:pk>/",
         views.students_detail_view,
         name="students-detail"),
    path("students/<int:pk>/del/",
         views.delete_student_view,
         name="students-del"),
    path("teachers/", views.teachers_view, name="teachers"),
    path("teachers/<int:pk>/",
         views.teachers_detail_view,
         name="teachers-detail"),
    path("teachers/<int:pk>/del/",
         views.delete_teacher_view,
         name="teachers-del"),
    path("courses/", views.subjects_view, name="subjects"),
    path("courses/<int:pk>/",
         views.subjects_detail_view,
         name="subjects-detail"),
    path("courses/<int:pk>/del/",
         views.delete_subject_view,
         name="subjects-del"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/change-password/",
         views.password_change_view,
         name="change-password"),
]
