from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse_lazy, resolve, reverse
from django.contrib.auth import get_user_model
from random import choices
from string import ascii_letters

from api.viewsets import (UsersViewSet, 
                          StudentsViewSet, 
                          TeachersViewSet, 
                          ClassesViewSet, 
                          ExamsViewSet, 
                          ArticlesViewSet, 
                          AssignmentsViewSet)
from mainapp.models import (Assignment, Grade, Student, 
                            Subject, 
                            Class, 
                            Exam,
                            Article)
from teachers.models import Teacher
from supports.models import School


def random_string(length:int=10):
    """    Generate a random string of fixed length. The length
    should not exceed 50.
    """
    assert length > 0 and length <= 50, "Invalid length."
    return "".join(choices(ascii_letters, k=length))


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


class PostAPISTests(APITestCase):
    def setUp(self):
        self.principal_user = self._create_user()
        self.school = self._create_school(support=self.principal_user)
        self.teacher = self._create_teacher()
        self.student = self._create_student()
        
    def _create_user(self, user_type:str="SS"):
        a = get_user_model().objects.create(
            username=random_string(),
            first_name=random_string(),
            last_name=random_string(),
            password=random_string(),
            user_type=user_type,
        )
        return a
    
    def _create_class(self):
        return Class.objects.create(class_id=random_string(), 
                                    school=self.school)
        
    def _create_school(self, support=None):
        if support is None:
            support = self._create_user("SS")
        return School.objects.create(name=random_string(), 
                                     support=support)
    
    def _create_teacher(self, user=None):
        if user is None:
            user = self._create_user(user_type="T")
        assert user.user_type == "T", "Invalid user type"
        return Teacher.objects.create(user=user, school=self.school)
    
    def _create_student(self, user=None, student_class=None):
        if user is None:
            user = self._create_user(user_type="S")
        if student_class is None:
            student_class = self._create_class()
        return Student.objects.create(user=user, student_class=student_class)
    
    def _create_subject(self, teacher=None, subject_name=None):
        if teacher is None:
            teacher = self._create_teacher()
        if subject_name is None:
            subject_name = random_string()
        return Subject.objects.create(teacher=teacher, name=subject_name)
    
    def test_accessibility_and_authorization_success(self):
        self.client.force_login(self.principal_user)
        basenames = [
            "students",
            "users",
            "classes",
            "exams",
            "articles",
            "assignments",
            "teachers",
            "grades",
        ]
        urls = [f"api:{basename}-list" for basename in basenames]
        for url in urls:
            response = self.client.post(data={"hello": "hello"}, 
                             path=reverse(url), 
                             format="json")
            self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            
    def test_accessibility_and_authorization_failure(self):
        basenames = [
            "students",
            "users",
            "classes",
            "exams",
            "articles",
            "assignments",
            "teachers",
            "grades",
        ]
        urls = [f"api:{basename}-list" for basename in basenames]
        for url in urls:
            response = self.client.post(data={"hello": "hello"}, 
                             path=reverse(url), 
                             format="json")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_post_student(self):
        initial_student_count = Student.objects.count()
        self.client.force_login(self.principal_user)
        url = reverse_lazy("api:students-list")
        student_user = self._create_user()
        student_class = self._create_class()
        data = {
            "user": student_user.pk,
            "student_class": student_class.pk,
        }
        response = self.client.post(data=data, path=url, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(), 
                         initial_student_count + 1)
        
    def test_post_teachers(self):
        initial_teacher_count = Teacher.objects.count()
        self.client.force_login(self.principal_user)
        url = reverse_lazy("api:teachers-list")
        teacher_user = self._create_user(user_type="T")
        data = {
            "user": teacher_user.pk,
            "school": self.school.pk,
        }
        response = self.client.post(path=url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Teacher.objects.count(), initial_teacher_count + 1)
        
    def test_post_user(self):
        initial_user_count = get_user_model().objects.count()
        self.client.force_login(self.principal_user)
        url = reverse_lazy("api:users-list")
        data = {
            "username": random_string(),
            "first_name": random_string(),
            "last_name": random_string(),
            "password": random_string(),
            "user_type": "SS",
            
        }
        response = self.client.post(path=url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(get_user_model().objects.count(), initial_user_count + 1)
        
    def test_post_classes(self):
        initial_class_count = Class.objects.count()
        self.client.force_login(self.principal_user)
        url = reverse_lazy("api:classes-list")
        data = {
            "class_id": random_string(),
            "school": self.school.pk,
        }        
        response = self.client.post(path=url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Class.objects.count(), initial_class_count + 1)
        
    def test_post_exams(self):
        initial_exam_count = Exam.objects.count()
        self.client.force_login(self.principal_user)
        url = reverse_lazy("api:exams-list")
        exam_subject = self._create_subject()
        teacher = self.teacher
        exam_class = self._create_class()
        exam_class.subjects.add(exam_subject)
        data = {
            "subject": exam_subject.pk,
            "teacher": teacher.pk,
            "exam_class": exam_class.pk,  
            "timestamp": "2023-01-01" 
        }
        response = self.client.post(path=url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Exam.objects.count(), initial_exam_count + 1)
        
    def test_post_article(self):
        initial_article_count = Article.objects.count()
        self.client.force_login(self.principal_user)
        url = reverse_lazy("api:articles-list")
        data = {
            "title": "Test Article",
            "categories": ["testing", "post", "api"],
            "text": "lorem ipsum dolor sit amet",
            "author": self.teacher.user.pk,
            "school": self.school.pk,
        }
        response = self.client.post(path=url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.count(), initial_article_count + 1)
        self.assertEqual(Article.objects.last().school, self.school)
    
    def test_post_assignment(self):
        initial_assignments_count = Assignment.objects.count()
        assignment_class = self._create_class()
        subject = self._create_subject()
        assignment_class.subjects.add(subject)
        body = ("lorem ipsum dolor sit amet consectetur adipiscing elit" 
                " sed do eiusmod tempor incididunt ut labore et dolore magna aliqua")
        url = reverse_lazy("api:assignments-list")
        self.client.force_login(self.principal_user)
        deadline = "2023-01-01"
        data = {
            "subject": subject,
            "assignment_class": assignment_class,
            "body": body,
            "deadline": deadline,
        }
        response = self.client.post(path=url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Assignment.objects.count(), initial_assignments_count + 1)
        
    def test_post_grade(self):    
        self.client.force_login(self.principal_user)
        initial_grade_count = Grade.objects.count()
        exam_subject = self._create_subject(self.teacher)
        exam_class = self._create_class()
        exam_class.subjects.add(exam_subject)
        exam = Exam.objects.create(subject=exam_subject, 
                                   exam_class=exam_class, 
                                   timestamp="2023-01-01",
                                   teacher=self.teacher)
        student = self._create_student(student_class=exam_class)
        url = reverse_lazy("api:grades-list")
        data = {
            "exam": exam.pk,
            "student": student.pk,
            "grade": 19.00,
        }
        response = self.client.post(path=url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Grade.objects.count(), initial_grade_count + 1)
    