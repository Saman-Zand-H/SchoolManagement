from rest_framework.routers import DefaultRouter
from django.urls import path

from . import viewsets


app_name = 'api'

router = DefaultRouter()
router.get_api_root_view().cls.__name__ = 'HomePage'
router.get_api_root_view().cls.__doc__ = ''
router.register(
    prefix="students", 
    viewset=viewsets.StudentsViewSet, 
    basename="students",
)
router.register(
    prefix="users", 
    viewset=viewsets.UsersViewSet, 
    basename="users",
)
router.register(
    prefix="classes", 
    viewset=viewsets.ClassesViewSet, 
    basename="classes",
)
router.register(
    prefix="exams", 
    viewset=viewsets.ExamsViewSet, 
    basename="exams",
)
router.register(
    prefix="articles", 
    viewset=viewsets.ArticlesViewSet, 
    basename="articles",
)
router.register(
    prefix="assignments", 
    viewset=viewsets.AssignmentsViewSet, 
    basename="assignments",
)
router.register(
    prefix="teachers", 
    viewset=viewsets.TeachersViewSet, 
    basename="teachers",
)
router.register(
    prefix="grades", 
    viewset=viewsets.GradesViewSet, 
    basename="grades",
)

urlpatterns = router.urls