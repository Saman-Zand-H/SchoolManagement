from django.urls import reverse, resolve
from django.contrib.auth import get_user_model, get_user
from django.contrib.messages import get_messages

import pytest
from pytest_django.asserts import (assertTemplateNotUsed, 
                                   assertTemplateUsed, 
                                   assertRedirects)
from datetime import date

from .views import (DashboardView, 
                    ExamsListView, 
                    SetGradesView, 
                    DeleteExamView, 
                    ClassesView, 
                    StudentsView,
                    StudentsDetailView,
                    ProfileView)
from mainapp.models import (Teacher, 
                            School, 
                            Class, 
                            Subject, 
                            Exam, 
                            Student,
                            Grade)


################## Fixture Factories ##################
@pytest.fixture
def school_factory(db):
    def create_support(
            user_id,
            school_name,
            first_name="name",
            last_name="name",
            phone_number="01223334455",
            password="test123456789"):
        user = get_user_model().objects.create_user(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            password=password,
            user_type="T")
        school = School.objects.create(name=school_name, support=user)
        return school
    return create_support


@pytest.fixture
def class_factory(db):
    def create_class(class_id, school):
        return Class.objects.create(class_id=class_id, school=school)
    return create_class


@pytest.fixture
def student_factory(db):
    def create_student(
            user_id,
            student_class,
            first_name="name",
            last_name="name",
            phone_number="01223334458",
            password="test123456789"):
        user = get_user_model().objects.create_user(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            password=password,
            user_type="S",
        )
        student = Student.objects.create(user=user, student_class=student_class)
        return student
    return create_student


@pytest.fixture
def teacher_factory(db):
    def create_teacher(
        user_id,
        school,
        first_name="name",
        last_name="name",
        phone_number="01223334455",
        password="test123456789"):
        user = get_user_model().objects.create_user(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            password=password,
            user_type="T",
        )
        teacher = Teacher.objects.create(user=user, school=school)
        return teacher
    return create_teacher


@pytest.fixture
def subject_factory(db):
    def create_subject(name, teacher):
        return Subject.objects.create(name=name, teacher=teacher)
    return create_subject


@pytest.fixture
def exam_factory(db):
    def create_exam(subject,
                    teacher,
                    exam_class,
                    timestamp=date(2021, 2, 2)):
        exam = Exam.objects.create(subject=subject,
                                    teacher=teacher,
                                    exam_class=exam_class,
                                    timestamp=timestamp)
        return exam
    return create_exam


################## Fixtures ##################
@pytest.fixture
def school_1(db, school_factory):
    return school_factory("support_1", "school_1")


@pytest.fixture
def student_1(db, student_factory, class_1):
    return student_factory("student_1", class_1)


@pytest.fixture
def teacher_1(db, teacher_factory, school_1):
    return teacher_factory("teacher_1", school_1)


@pytest.fixture
def subject_1(db, subject_factory, teacher_1):
    return subject_factory("test_subject", teacher_1)


@pytest.fixture
def class_1(db, class_factory, school_1, subject_1):
    class_instance = class_factory("test_class_1", school_1)
    class_instance.subjects.add(subject_1)
    return class_instance


@pytest.fixture
def exam_1(db, exam_factory, subject_1, teacher_1, class_1):
    return exam_factory(subject_1, teacher_1, class_1)


################## Test Access ##################
def test_teachers_homepage_is_proccessed_as_expected():
    url = reverse("teachers:home")
    assert url == "/teachers/", "url name is not set properly"
    assert resolve(url).func.__name__ == DashboardView.__name__, "unexpected view is used"


def test_authenticated_support_access_is_forbidden(client, school_1):
    client.force_login(school_1.support)
    url = reverse("teachers:home")
    assert get_user(client).is_authenticated == True, "login is not working"
    response = client.get(url)
    assert response.status_code == 403, "permissions are not working correctly"
    assertTemplateUsed(response, "errors/403.html", "This template is not used")


def test_authenticated_teacher_can_access(client, teacher_1):
    url = reverse("teachers:home")
    client.force_login(teacher_1.user)
    assert get_user(client).is_authenticated == True
    response = client.get(url)
    assert response.status_code == 200
    assert resolve(url).func.__name__ == DashboardView.__name__
    assertTemplateUsed(response, "dashboard/teachers/index.html")


################## Test App ##################
def test_exams_list_page_is_proccessed_as_expected(client, teacher_1):
    client.force_login(teacher_1.user)

    url = reverse("teachers:exams")
    assert url == "/teachers/exams/"
    response = client.get(url)

    assert response.status_code == 200
    assert resolve(url).func.__name__ == ExamsListView.__name__
    assertTemplateUsed(response, "dashboard/teachers/exams.html")


def test_create_exam_successful(client, teacher_1, class_1, subject_1):
    client.force_login(teacher_1.user)

    assert Exam.objects.count() == 0
    url = reverse("teachers:exams")
    assert url == "/teachers/exams/"
    assert resolve(url).func.__name__ == ExamsListView.__name__
    data = {"subject": class_1.pk,
            "exam_class": subject_1.pk,
            "teacher": teacher_1,
            "full_score": 20.0,
            "timestamp": "03/03/2020"}
    response = client.post(url, data)
    messages = [*get_messages(response.wsgi_request)]
    created_exam = Exam.objects.last()

    assert response.status_code == 302
    assertRedirects(response, url)
    assert str(messages[-1]) == "Exam created successfully."
    
    assert Exam.objects.count() == 1
    assert created_exam.teacher == teacher_1
    assert created_exam.exam_class == class_1
    assert created_exam.subject == subject_1


def test_create_exam_unsuccessful(client, teacher_1):
    client.force_login(teacher_1.user)

    assert Exam.objects.count() == 0
    url = reverse("teachers:exams")
    data = {
        "subject": "lakjlkdjf",
        "exam_class": 255252525251,
        "teacher": 554565852,
        "full_score": 20.0,
        "timestamp": "03/031919",
    }
    response = client.post(url, data)
    messages = [*get_messages(response.wsgi_request)]

    assert Exam.objects.count() == 0
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/teachers/exams.html")
    assert str(messages[-1]) == "Provided inputs are invalid."


def test_set_exam_grades_successful(client, teacher_1, class_1, subject_1, student_1):
    client.force_login(teacher_1.user)

    exams_url = reverse("teachers:exams")
    data = {
        "subject": class_1.pk,
        "exam_class": subject_1.pk,
        "teacher": teacher_1,
        "full_score": 20.0,
        "timestamp": "04/03/2020",
    }
    client.post(exams_url, data)
    exam = Exam.objects.last()
    
    url = reverse("teachers:exams-detail", kwargs={"pk": exam.pk})
    assert url == exam.get_absolute_url()
    assert resolve(url).func.__name__ == SetGradesView.__name__
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/teachers/grades.html")

    assert exam.grade_exam.count() == 0
    data = {"form-TOTAL_FORMS": 1,
            "form-INITIAL_FORMS": 0,
            "form-MIN_NUM_FORMS": 0,
            "form-MAX_NUM_FORMS": 1,
            "form-0-id": '',
            "form-0-grade": 0.0,
            "form-0-student": student_1.pk,
            "form-0-exam": exam.pk}
    response = client.post(url, data)
    grade = Grade.objects.last()
    messages = [*get_messages(response.wsgi_request)]

    assert str(messages[-1]) == "Grades submitted successfully."
    assert response.status_code == 302
    assertRedirects(response, url)

    assert exam.grade_exam.count() == 1
    assert grade.exam == exam
    assert grade.student == student_1
    assert grade.grade == 0.0


def test_set_exam_grades_unsuccessful(client, teacher_1, class_1, subject_1, student_1):
    client.force_login(teacher_1.user)

    exams_url = reverse("teachers:exams")
    data = {
        "subject": class_1.pk,
        "exam_class": subject_1.pk,
        "teacher": teacher_1,
        "full_score": 20.0,
        "timestamp": "04/03/2020",
    }
    client.post(exams_url, data)
    exam = Exam.objects.last()
    
    url = reverse("teachers:exams-detail", kwargs={"pk": exam.pk})
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/teachers/grades.html")

    assert exam.grade_exam.count() == 0
    data = {"form-TOTAL_FORMS": 1,
            "form-INITIAL_FORMS": 0,
            "form-MIN_NUM_FORMS": 0,
            "form-MAX_NUM_FORMS": 1,
            "form-0-id": '',
            "form-0-grade": 21.0,       # Invalid input
            "form-0-student": student_1.pk,
            "form-0-exam": exam.pk}
    response = client.post(url, data)
    messages = [*get_messages(response.wsgi_request)]

    assert str(messages[-1]) == "Grades cannot exceed the full score."
    assert response.status_code == 302
    assertRedirects(response, url)
    assert exam.grade_exam.count() == 0

    data = {"form-TOTAL_FORMS": 1,
            "form-INITIAL_FORMS": 0,
            "form-MIN_NUM_FORMS": 0,
            "form-MAX_NUM_FORMS": 1,
            "form-0-id": '',
            "form-0-grade": 20.0,
            "form-0-student": "jlakjsldfm,asn",         # Invalid input
            "form-0-exam": 25754789878}         # Invalid input
    response = client.post(url, data)
    messages = [*get_messages(response.wsgi_request)]

    assert str(messages[-1]) == "Provided inputs are invalid."
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/teachers/grades.html")
    assert exam.grade_exam.count() == 0


def test_delete_exam(client, teacher_1, student_1, exam_1):
    client.force_login(teacher_1.user)

    assert Grade.objects.count() == 0
    url = reverse("teachers:exams-detail", kwargs={"pk": exam_1.pk})
    data = {"form-TOTAL_FORMS": 1,
            "form-INITIAL_FORMS": 0,
            "form-MIN_NUM_FORMS": 0,
            "form-MAX_NUM_FORMS": 1,
            "form-0-id": '',
            "form-0-grade": 0.0,
            "form-0-student": student_1.pk,
            "form-0-exam": exam_1.pk}
    client.post(url, data)
    assert Grade.objects.count() == 1

    url = reverse("teachers:del-exam", kwargs={"pk": exam_1.pk})
    assert url == f"/teachers/exams/{exam_1.pk}/del/"
    assert resolve(url).func.__name__ == DeleteExamView.__name__

    response = client.get(url)
    messages = [*get_messages(response.wsgi_request)]

    assert response.status_code == 302
    assertRedirects(response, reverse("teachers:exams"))
    assert str(messages[-1]) == "Exam is deleted successfully."

    assert Exam.objects.count() == 0
    assert Grade.objects.count() == 0


def test_classes_page(client, teacher_1):
    client.force_login(teacher_1.user)

    url = reverse("teachers:classes")
    assert url == "/teachers/classes/"
    assert resolve(url).func.__name__ == ClassesView.__name__

    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/teachers/classes.html")


def test_students_page(client, teacher_1, student_1):
    client.force_login(teacher_1.user)

    url = reverse("teachers:students")
    assert url == "/teachers/students/"
    assert resolve(url).func.__name__ == StudentsView.__name__

    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/teachers/students.html")

    url = reverse("teachers:students-detail", kwargs={"pk": student_1.pk})
    response = client.get(url)

    assert response.status_code == 200
    assert resolve(url).func.__name__ == StudentsDetailView.__name__
    assertTemplateUsed("dashboard/teachers/students_detail.html")


def test_profile_page(client, teacher_1):
    client.force_login(teacher_1.user)

    url = reverse("teachers:profile")
    assert url == "/teachers/profile/"
    assert resolve(url).func.__name__ == ProfileView.__name__

    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/teachers/profile.html")

    assert get_user(client).about == ""
    response = client.post(url, {"about": "Hello from my Django world!"})
    messages = [*get_messages(response.wsgi_request)]

    assert response.status_code == 302
    assertRedirects(response, url)
    assert str(messages[-1]) == "User bio updated successfully."
    assert get_user(client).about == "Hello from my Django world!"
