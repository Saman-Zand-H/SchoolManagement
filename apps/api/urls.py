from rest_framework.routers import DefaultRouter
from django.urls import path

from . import viewsets, views


app_name = 'api'

router = DefaultRouter()
router.get_api_root_view().cls.__name__ = 'HomePage'
router.get_api_root_view().cls.__doc__ = ''
router.register("students", viewsets.StudentsViewSet, basename="students")
router.register("users", viewsets.UsersViewSet, basename="users")
router.register("classes", viewsets.ClassesViewSet, basename="classes")
router.register("exams", viewsets.ExamsViewSet, basename="exams")
router.register("articles", viewsets.ArticlesViewSet, basename="articles")
router.register("assignments", viewsets.AssignmentsViewSet, basename="assignments")
router.register("teachers", viewsets.TeachersViewSet, basename="teachers")

urlpatterns = [
    path(
        route='grades/<int:pk>',
        view=views.GradesDetailView.as_view(),
        name="grades-detail",
    )
] + router.urls