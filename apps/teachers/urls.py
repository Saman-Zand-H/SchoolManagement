from django.urls import path

from . import views

app_name = "teachers"

urlpatterns = [
    path("", views.dashboard_view, name="home"),
    path("exams/", views.exams_list_view, name="exams"),
    path("ajax/exams/create/", views.ajax_create_exam, name="ajax-add-exam"),
    path("ajax/exams/filter/", views.ajax_filter_exam,
         name="ajax-filter-exam"),
    path("exams/<int:pk>/", views.set_grades_view, name="exams-detail"),
    path("exams/<int:pk>/del/", views.delete_exam_view, name="del-exam"),
    path("students/", views.students_view, name="students"),
    path("students/<int:pk>",
         views.students_detail_view,
         name="students-detail"),
    path("classes/", views.classes_view, name="classes"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/change-password/",
         views.change_password_view,
         name="change-password"),
    path("articles/", views.articles_template_view, name="articles"),
    path("articles/add/", views.add_article_view, name="add-articles"),
    path("articles/<int:pk>", views.article_detail_view,
         name="article-detail"),
    path("articles/del/<int:pk>",
         views.delete_article_view,
         name="del-article"),
]
