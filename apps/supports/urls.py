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
    path("students/", views.students_view, name="students"),
    path("students/<int:pk>/",
         views.students_detail_view,
         name="students-detail"),
    path("teachers/", views.teachers_view, name="teachers"),
    path("teachers/<int:pk>/",
         views.teachers_detail_view,
         name="teachers-detail"),
    path("courses/", views.subjects_view, name="subjects"),
    path("courses/<int:pk>/",
         views.subjects_detail_view,
         name="subjects-detail"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/change-password/",
         views.password_change_view,
         name="change-password"),
    path("articles/", views.articles_template_view, name="articles"),
    path("articles/<int:pk>/",
         views.article_detail_view,
         name="article-detail"),
    path("articles/add/", views.add_article_view, name="add-articles"),
    path("articles/del/<int:pk>",
         views.delete_article_view,
         name="del-article"),
]
