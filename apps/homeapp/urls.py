from django.urls import path

from . import views

app_name = "home"

urlpatterns = [
    path("", views.homepageview, name="home"),
    path("support-page/", views.support_view, name="support-page"),
    path("set-language/", views.set_language, name="set_language"),
    path("articles/", views.articles_template_view, name="articles"),
    path("articles/<int:pk>/",
         views.article_detail_view,
         name="article-detail"),
    path("articles/add/", views.add_article_view, name="add-article"),
    path("assignments/", views.assignments_view, name="assignments"),
    path("assignments/add", views.add_assignment_view, name="add-assignment"),
    path("assignments/<int:pk>/", views.assignment_detail_view, name="assignment-detail"),
]
