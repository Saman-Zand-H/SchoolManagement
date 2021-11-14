from django.contrib.auth import get_user_model, get_user
from django.urls import resolve, reverse
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile

import pytest
from pytest_django.asserts import assertRedirects, assertTemplateNotUsed, assertTemplateUsed
import pathlib

from mainapp.models import Class, Subject, Student
from supports.views import (CreateSchoolView, HomeView, ClassesView,
                            ClassesDetailView, SubjectsView,
                            SubjectsDetailView, DeleteSubject, TeachersView,
                            TeachersDetailView, DeleteTeacher, StudentsView,
                            StudentsDetailView, DeleteStudent)
from supports.models import School
from teachers.models import Teacher


################## Fixture Factories ##################
@pytest.fixture
def user_factory(db):
    def create_user(user_id,
                    first_name="name",
                    last_name="name",
                    phone_number="01223334455",
                    password="test123456789"):
        user = get_user_model().objects.create_user(user_id=user_id,
                                                    first_name=first_name,
                                                    last_name=last_name,
                                                    phone_number=phone_number,
                                                    password=password,
                                                    email=None,
                                                    user_type="SS")
        return user

    return create_user


@pytest.fixture
def teacher_factory(db):
    def create_teacher(user_id,
                       school,
                       first_name="Test",
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
        return Teacher.objects.create(user=user, school=school)

    return create_teacher


@pytest.fixture
def subject_factory(db):
    def create_subject(name, teacher):
        return Subject.objects.create(name=name, teacher=teacher)

    return create_subject


@pytest.fixture
def class_factory(db):
    def create_class(class_id, school):
        return Class.objects.create(class_id=class_id, school=school)

    return create_class


@pytest.fixture
def student_factory(db):
    def create_student(user_id,
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
        student = Student.objects.create(user=user,
                                         student_class=student_class)
        return student

    return create_student


################## Fixtures ##################
@pytest.fixture
def support_1(db, user_factory):
    return user_factory("support_test1")


@pytest.fixture
def school_1(db, support_1):
    return School.objects.create(name="test_school1", support=support_1)


@pytest.fixture
def teacher_1(db, teacher_factory, school_1):
    return teacher_factory("test_teacher1", school_1)


@pytest.fixture
def subject_1(db, subject_factory, teacher_1):
    return subject_factory("test_subject", teacher_1)


@pytest.fixture
def subject_2(db, subject_factory, teacher_1):
    return subject_factory("test_subject1", teacher_1)


@pytest.fixture
def class_1(db, class_factory, school_1):
    class_instance = class_factory("test_class_1", school_1)
    return class_instance


@pytest.fixture
def class_2(db, class_factory, school_1):
    class_instance = class_factory("test_class_2", school_1)
    return class_instance


@pytest.fixture
def student_1(db, student_factory, class_1):
    return student_factory("student_1", class_1)


################## Test Access ##################
def test_homepage():
    url = reverse("supports:home")
    assert url == "/support/"
    assert resolve(url).func.__name__ == HomeView.__name__


def test_teachers_access_is_forbidden(client, teacher_1):
    client.force_login(teacher_1.user)
    url = reverse("supports:home")
    response = client.get(url)
    assert response.status_code == 403
    assertTemplateUsed(response, "errors/403.html")


def test_unauthenticated_users_access_is_forbidden(db, client):
    url = reverse("supports:home")
    response = client.get(url)
    assert response.status_code != 200
    assertTemplateNotUsed(response, "dashboard/supports/")
    assert response.status_code == 302
    assertRedirects(response, reverse("account_login"))


def test_authenticated_support_can_pass(client, school_1):
    client.force_login(school_1.support)
    url = reverse("supports:home")
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/supports/index.html")


################## Test App ##################
def test_school_registration(client, support_1):
    client.force_login(support_1)

    assert School.objects.count() == 0
    url = reverse("supports:create-school")
    assert url == "/support/account/signup/school/"
    assert resolve(url).func.__name__ == CreateSchoolView.__name__

    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "account/register_school.html")

    response = client.post(url, {
        "name": "test_school",
        "support": support_1.pk
    })
    messages = [*get_messages(response.wsgi_request)]
    school = School.objects.last()

    assert response.status_code == 302
    assertRedirects(response, reverse("home:home"))
    assert str(messages[-1]) == "You registered successfully."

    assert School.objects.count() == 1
    assert school.support == get_user(client)
    assert school.name == "test_school"


def test_create_class_successful(client, school_1, subject_1):
    client.force_login(school_1.support)

    assert Class.objects.count() == 0
    url = reverse("supports:classes")
    assert url == "/support/classes/"
    assert resolve(url).func.__name__ == ClassesView.__name__

    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/supports/classes.html")

    response = client.post(url, {
        "class_id": "test_class",
        "subjects": subject_1.pk
    })
    messages = [*get_messages(response.wsgi_request)]
    created_class = Class.objects.last()

    assert response.status_code == 302
    assertRedirects(response, url)
    assert str(messages[-1]) == "Class saved successfully."

    assert Class.objects.count() == 1
    assert created_class.class_id == "test_class"
    assert created_class.subjects.count() == 1
    assert created_class.subjects.first().name == subject_1.name
    assert created_class.school == school_1


def test_create_class_unsuccessful(client, school_1):
    client.force_login(school_1.support)

    assert Class.objects.count() == 0
    url = reverse("supports:classes")
    response = client.post(url, {
        "class_id": 20242.25,
        "school": ";TEST_SCHOOL",
        "subject": "TEST_SUBJECT"
    })
    messages = [*get_messages(response.wsgi_request)]
    created_class = Class.objects.last()

    assert created_class is None
    assert Class.objects.count() == 0
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/supports/classes.html")
    assert str(messages[-1]) == "Provided inputs are invalid."


def test_class_details(client, school_1, subject_1, subject_2, class_1):
    client.force_login(school_1.support)

    url = reverse("supports:classes-detail", kwargs={"pk": class_1.pk})
    assert url == class_1.get_absolute_url()
    assert resolve(url).func.__name__ == ClassesDetailView.__name__

    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/supports/classes_detail.html")

    data = {
        "class_id": "test_class_alt",
        "subjects": [subject_1.pk, subject_2.pk]
    }
    response = client.post(url, data)
    messages = [*get_messages(response.wsgi_request)]
    edited_class = Class.objects.last()

    assert response.status_code == 302
    assertRedirects(response, url)
    assert str(messages[-1]) == "Class updated successfully."

    assert class_1.pk == edited_class.pk
    assert edited_class.class_id != class_1.class_id
    assert edited_class.class_id == "test_class_alt"
    assert edited_class.subjects.count() == 2
    assert [subject_1, subject_2] == [*edited_class.subjects.all()]

    url = reverse("supports:classes-del", kwargs={"pk": edited_class.pk})
    response = client.get(url)
    messages = [*get_messages(response.wsgi_request)]

    assert response.status_code == 302
    assertRedirects(response, reverse("supports:classes"))
    assert str(messages[-1]) == "Class deleted successfully."
    assert Class.objects.count() == 0


def test_create_subject_successful(client, school_1, teacher_1):
    client.force_login(school_1.support)

    url = reverse("supports:subjects")
    assert url == "/support/courses/"
    assert resolve(url).func.__name__ == SubjectsView.__name__

    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/supports/subjects.html")

    assert Subject.objects.count() == 0
    response = client.post(url, {
        "name": "test_subject",
        "teacher": teacher_1.pk
    })
    created_subject = Subject.objects.last()
    messages = [*get_messages(response.wsgi_request)]

    assert response.status_code == 302
    assertRedirects(response, url)
    assert str(messages[-1]) == "Course created successfully."

    assert Subject.objects.count() == 1
    assert created_subject.name == "test_subject"
    assert created_subject.teacher == teacher_1


def test_create_subject_unsuccessful(client, school_1):
    client.force_login(school_1.support)

    url = reverse("supports:subjects")
    assert Subject.objects.count() == 0

    response = client.post(url, {
        "name": "test_subject",
        "teacher": "TEST_TEACHER"
    })
    created_subject = Subject.objects.last()
    messages = [*get_messages(response.wsgi_request)]

    assert created_subject is None
    assert Subject.objects.count() == 0
    assert str(messages[-1]) == "Provided inputs are invalid."


def test_subjects_detail(client, school_1, subject_1):
    client.force_login(school_1.support)

    url = reverse("supports:subjects-detail", kwargs={"pk": subject_1.pk})
    assert url == subject_1.get_absolute_url()
    assert resolve(url).func.__name__ == SubjectsDetailView.__name__

    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/supports/subjects_detail.html")

    url = reverse("supports:subjects-del", kwargs={"pk": subject_1.pk})
    assert url == f"/support/courses/{subject_1.pk}/del/"
    assert resolve(url).func.__name__ == DeleteSubject.__name__

    assert Subject.objects.count() == 1
    response = client.get(url)
    messages = [*get_messages(response.wsgi_request)]

    assert response.status_code == 302
    assertRedirects(response, reverse("supports:subjects"))
    assert str(messages[-1]) == "Course deleted successfully."
    assert Subject.objects.count() == 0


def test_create_teacher_successful(client, school_1):
    client.force_login(school_1.support)

    url = reverse("supports:teachers")
    assert url == "/support/teachers/"
    assert resolve(url).func.__name__ == TeachersView.__name__

    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/supports/teachers.html")

    picture_path = pathlib.Path.cwd() / "media" / "empty-profile.jpg"
    data = {
        "username":
        "test_created_teacher",
        "first_name":
        "first_name",
        "last_name":
        "last_name",
        "password1":
        "test123456",
        "password2":
        "test123456",
        "phone_number":
        "09226761449",
        "user_type":
        "T",
        "picture":
        SimpleUploadedFile(name='empty-profile.jpg',
                           content=open(picture_path, 'rb').read(),
                           content_type='image/jpeg'),
    }
    response = client.post(url, data)
    created_teacher = Teacher.objects.last()
    messages = [*get_messages(response.wsgi_request)]

    assert response.status_code == 302
    assertRedirects(response, url)
    assert str(messages[-1]) == "Teacher created successfully."

    assert Teacher.objects.count() == 1
    assert created_teacher.user.user_id == "test_created_teacher"


def test_create_teacher_unsuccessful(client, school_1):
    client.force_login(school_1.support)

    url = reverse("supports:teachers")
    picture_path = pathlib.Path.cwd() / "static" / "assets" / "img" / \
        "icons" / "common" / "github.svg"
    data = {
        "username":
        "test_created_teacher",
        "first_name":
        "first_name",
        "last_name":
        "last_name",
        "password1":
        "test123456",
        "password2":
        "test123456",
        "phone_number":
        "09226761449",
        "user_type":
        "T",
        "picture":
        SimpleUploadedFile(name='github.svg',
                           content=open(picture_path, 'rb').read(),
                           content_type='image/svg')
    }  # Invalid file extension
    response = client.post(url, data)
    created_teacher = Teacher.objects.last()
    messages = [*get_messages(response.wsgi_request)]

    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/supports/teachers.html")
    assert str(messages[-1]) == "Provided inputs are invalid."
    assert created_teacher is None
    assert Teacher.objects.count() == 0


def test_teachers_detail_successful(client, school_1, teacher_1):
    client.force_login(school_1.support)

    url = reverse("supports:teachers-detail", kwargs={"pk": teacher_1.pk})
    assert url == teacher_1.get_absolute_url()
    assert resolve(url).func.__name__ == TeachersDetailView.__name__

    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/supports/teachers_detail.html")

    data = {
        "university": "TITS(Texas Institute of Technology and Science)",
        "degree": "PhD in Software Engineering",
        "phone_number": "01336669988"
    }
    response = client.post(url, data)
    messages = [*get_messages(response.wsgi_request)]
    edited_teacher = Teacher.objects.last()

    assert response.status_code == 302
    assertRedirects(response, url)
    assert str(messages[-1]) == "Changes saved successfully."

    assert edited_teacher.pk == teacher_1.pk
    assert edited_teacher.user.phone_number == "01336669988"
    assert edited_teacher.degree == "PhD in Software Engineering"
    assert edited_teacher.university == "TITS(Texas Institute of Technology and Science)"

    url = reverse("supports:teachers-del", kwargs={"pk": teacher_1.user.pk})
    assert url == f"/support/teachers/{teacher_1.user.pk}/del/"
    assert resolve(url).func.__name__ == DeleteTeacher.__name__

    response = client.get(url)
    messages = [*get_messages(response.wsgi_request)]

    assert response.status_code == 302
    assertRedirects(response, reverse("supports:teachers"))
    assert str(messages[-1]) == "Teacher deleted successfully."
    assert Teacher.objects.count() == 0


def test_create_student_successful(client, school_1, class_1):
    client.force_login(school_1.support)

    url = reverse("supports:students")
    assert url == "/support/students/"
    assert resolve(url).func.__name__ == StudentsView.__name__

    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/supports/students.html")

    assert Student.objects.count() == 0
    data = {
        "username": "test_created_student",
        "first_name": "first_name",
        "last_name": "last_name",
        "password1": "test123456",
        "password2": "test123456",
        "phone_number": "09226761449",
        "user_type": "S",
        "student_class": class_1.pk
    }
    response = client.post(url, data)
    messages = [*get_messages(response.wsgi_request)]
    created_student = Student.objects.last()

    assert response.status_code == 302
    assertRedirects(response, url)
    assert str(messages[-1]) == "Student created successfully."

    assert Student.objects.count() == 1
    assert created_student.student_class == class_1
    assert created_student.user.user_id == "test_created_student"


def test_create_student_unsuccessful(client, school_1):
    client.force_login(school_1.support)
    url = reverse("supports:students")

    assert Student.objects.count() == 0
    data = {
        "username": "test_created_student",
        "first_name": "first_name",
        "last_name": "last_name",
        "password1": "test123456",
        "password2": "test123456",
        "phone_number": "09226755461449",  # Invalid phonenumber
        "user_type": "S",
        "student_class": "TEST_CLASS"
    }  # Invalid class
    response = client.post(url, data)
    messages = [*get_messages(response.wsgi_request)]
    created_student = Student.objects.last()

    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/supports/students.html")
    assert str(messages[-1]) == "Provided inputs are invalid."
    assert created_student is None
    assert Student.objects.count() == 0


def test_students_detail(client, school_1, student_1, class_2):
    client.force_login(school_1.support)

    url = reverse("supports:students-detail", kwargs={"pk": student_1.pk})
    assert url == student_1.get_absolute_url_supports()
    assert resolve(url).func.__name__ == StudentsDetailView.__name__

    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/supports/students_detail.html")

    response = client.post(url, {
        "phone_number": "09998887744",
        "student_class": class_2.pk
    })
    messages = [*get_messages(response.wsgi_request)]
    edited_student = Student.objects.last()

    assert response.status_code == 302
    assertRedirects(response, url)
    assert str(messages[-1]) == "Student updated successfully."

    assert edited_student.pk == student_1.pk
    assert edited_student.student_class == class_2
    assert edited_student.user.phone_number == "09998887744"

    url = reverse("supports:students-del",
                  kwargs={"pk": edited_student.user.pk})
    assert url == f"/support/students/{edited_student.user.pk}/del/"
    assert resolve(url).func.__name__ == DeleteStudent.__name__

    response = client.get(url)
    messages = [*get_messages(response.wsgi_request)]
    deleted_student = Student.objects.last()

    assert response.status_code == 302
    assertRedirects(response, reverse("supports:students"))
    assert str(messages[-1]) == "Student deleted successfully."
    assert Student.objects.count() == 0
    assert deleted_student is None
