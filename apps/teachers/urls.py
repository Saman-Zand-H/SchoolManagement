from django.urls import path

from . import views

app_name = "teachers"

urlpatterns = [
    path("", views.dashboardview, name="home"),
    path("exams/", views.examslistview, name="exams"),
    path("ajax/exams/create/", views.ajax_create_exam, name="ajax-add-exam"),
    path("ajax/exams/filter/", views.ajax_filter_exam,
         name="ajax-filter-exam"),
    path("exams/<int:pk>/", views.setgradesview, name="exams-detail"),
    path("exams/<int:pk>/del/", views.deleteexamview, name="del-exam"),
    path("students/", views.students_view, name="students"),
    path("students/<int:pk>",
         views.students_detailview,
         name="students-detail"),
    path("classes/", views.classesview, name="class"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
]
