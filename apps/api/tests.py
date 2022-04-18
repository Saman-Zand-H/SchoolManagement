from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse_lazy, resolve
from django.contrib.auth import get_user_model

from api.viewsets import (UsersViewSet, 
                          StudentsViewSet, 
                          TeachersViewSet, 
                          ClassesViewSet, 
                          ExamsViewSet, 
                          ArticlesViewSet, 
                          AssignmentsViewSet)
from mainapp.models import Student
from teachers.models import Teacher
from supports.models import School


class GetAPIsTests(APITestCase):
    fixtures = ["tests-fixture.json", "auth-fixture.json"]
    
    def setUp(self):
        self.principal_user = get_user_model().objects.first()
        self.school = School.objects.first()
        self.teacher = Teacher.objects.first()
        self.student = Student.objects.first()
        
    def _get_page_check_status_code_and_data_length(self, url, status_code, data_length):
        """
        Check status code and data length of the response.
        """
        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(len(response.data), data_length)
        
    def test_fail_anonymous_user(self):
        url = reverse_lazy("api:api-root")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_check_url_users(self):
        url = reverse_lazy("api:users-list")
        self.assertEqual(url, "/api/v1/users/")
        self.assertEqual(resolve(url).func.__name__, UsersViewSet.__name__)
        
    def test_get_users_apis_by_principal(self):
        self.client.force_login(self.principal_user)
        
        url = reverse_lazy("api:users-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 5)
    
    def test_get_users_apis_by_teacher(self):
        self.client.force_login(self.teacher.user)
        
        url = reverse_lazy("api:users-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 5)

    def test_get_users_apis_by_student(self):
        self.client.force_login(self.student.user)
        
        url = reverse_lazy("api:users-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 3)

    def test_check_url_students(self):
        url = reverse_lazy("api:students-list")
        self.assertEqual(url, "/api/v1/students/")
        self.assertEqual(resolve(url).func.__name__, StudentsViewSet.__name__)

    def test_get_students_by_principal(self):
        self.client.force_login(self.principal_user)
        
        url = reverse_lazy("api:students-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 2)
    
    def test_get_students_by_teacher(self):
        self.client.force_login(self.teacher.user)
        
        url = reverse_lazy("api:students-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 1)
        
    def test_get_students_by_student(self):
        self.client.force_login(self.student.user)
        
        url = reverse_lazy("api:students-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 1)
        
    def test_check_url_teachers(self):
        url = reverse_lazy("api:teachers-list")
        self.assertEqual(url, "/api/v1/teachers/")
        self.assertEqual(resolve(url).func.__name__, TeachersViewSet.__name__)
        
    def test_get_teachers_by_principal(self):
        self.client.force_login(self.principal_user)
        
        url = reverse_lazy("api:teachers-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 2)
        
    def test_get_teachers_by_teacher(self):
        self.client.force_login(self.teacher.user)
        
        url = reverse_lazy("api:teachers-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 2)
        
    def test_get_teachers_by_student(self):
        self.client.force_login(self.student.user)
        
        url = reverse_lazy("api:teachers-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 1)
        
    def test_check_url_classes(self):
        url = reverse_lazy("api:classes-list")
        self.assertEqual(url, "/api/v1/classes/")
        self.assertEqual(resolve(url).func.__name__, ClassesViewSet.__name__)
        
    def test_get_classes_by_principal(self):
        self.client.force_login(self.principal_user)
        
        url = reverse_lazy("api:classes-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 2)

    def test_get_classes_by_teacher(self):
        self.client.force_login(self.teacher.user)
        
        url = reverse_lazy("api:classes-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 1)
        
    def test_get_classes_by_student(self):
        self.client.force_login(self.student.user)
        
        url = reverse_lazy("api:classes-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 1)

    def test_check_url_exams(self):
        url = reverse_lazy("api:exams-list")
        self.assertEqual(url, "/api/v1/exams/")
        self.assertEqual(resolve(url).func.__name__, ExamsViewSet.__name__)
        
    def test_get_exams_by_principal(self):
        self.client.force_login(self.principal_user)
        
        url = reverse_lazy("api:exams-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 2)

    def test_get_exams_by_teacher(self):
        self.client.force_login(self.teacher.user)
        
        url = reverse_lazy("api:exams-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 1)
        
    def test_get_exams_by_student(self):
        self.client.force_login(self.student.user)
        
        url = reverse_lazy("api:exams-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 1)

    def test_check_url_articles(self):
        url = reverse_lazy("api:articles-list")
        self.assertEqual(url, "/api/v1/articles/")
        self.assertEqual(resolve(url).func.__name__, ArticlesViewSet.__name__)
        
    def test_get_articles_by_principal(self):
        self.client.force_login(self.principal_user)
        
        url = reverse_lazy("api:articles-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 2)
        
    def test_get_articles_by_teacher(self):
        self.client.force_login(self.teacher.user)
        
        url = reverse_lazy("api:articles-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 2)
        
    def test_get_articles_by_student(self):
        self.client.force_login(self.student.user)
        
        url = reverse_lazy("api:articles-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 2)
        
    def test_check_url_assignments(self):
        url = reverse_lazy("api:assignments-list")
        self.assertEqual(url, "/api/v1/assignments/")
        self.assertEqual(resolve(url).func.__name__, AssignmentsViewSet.__name__)
        
    def test_get_assignments_by_principal(self):
        self.client.force_login(self.principal_user)
        
        url = reverse_lazy("api:assignments-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 3)
        
    def test_get_assignments_by_teacher(self):
        self.client.force_login(self.teacher.user)
        
        url = reverse_lazy("api:assignments-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 2)
    
    def test_get_assignments_by_student(self):
        self.client.force_login(self.student.user)
        
        url = reverse_lazy("api:assignments-list")
        self._get_page_check_status_code_and_data_length(
            url, status.HTTP_200_OK, 2)
