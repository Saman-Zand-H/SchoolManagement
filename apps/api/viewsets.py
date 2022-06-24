from rest_framework.viewsets import  ModelViewSet
from django.contrib.auth import get_user_model

from .serializers import (ReadOnlyStudentsSerializer, 
                          ReadOnlyUsersSerializer, 
                          ReadOnlyClassesSerializer, 
                          ReadOnlyExamsSerializer,
                          ReadOnlyArticlesSerializer,
                          ReadOnlyAssignmentsSerializer,
                          ReadOnlyTeachersSerializer,
                          ReadOnlyGradesSerializer,
                          WriteOnlyStudentsSerializer, 
                          WriteOnlyUsersSerializer, 
                          WriteOnlyClassesSerializer, 
                          WriteOnlyExamsSerializer,
                          WriteOnlyArticlesSerializer,
                          WriteOnlyAssignmentsSerializer,
                          WriteOnlyTeachersSerializer,
                          WriteOnlyGradesSerializer)
from .permissions import CanCreate
from mainapp.models import (Grade, 
                            Student, 
                            Class, 
                            Exam, 
                            Article, 
                            Assignment)
from teachers.models import Teacher


class _BaseViewSet(ModelViewSet):
    permission_classes = [CanCreate]
    
    def get_serializer_class(self):
        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method."
            % self.__class__.__name__
        )
        assert self.writeonly_serializer_class is not None, (
            "'%s' should either include a `writeonly_serializer_class` attribute, "
            "or override the `get_serializer_class()` method."
            % self.__class__.__name__
        )
        if self.action in ["retrieve", "list"]:
            return self.serializer_class
        else:
            return self.writeonly_serializer_class


class StudentsViewSet(_BaseViewSet):
    serializer_class = ReadOnlyStudentsSerializer
    writeonly_serializer_class = WriteOnlyStudentsSerializer
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            match self.request.user.user_type:
                case "T":
                    return Student.objects.filter(
                        student_class__subjects__teacher__user=self.request.user
                    ).distinct()
                case "SS":
                    return Student.objects.filter(
                        student_class__school__support=self.request.user)
                case "S":
                    student_class = Student.objects.get(
                        user__username=self.request.user.username).student_class
                    return Student.objects.filter(student_class=student_class)
        return Student.objects.none()


class TeachersViewSet(_BaseViewSet):
    serializer_class = ReadOnlyTeachersSerializer
    writeonly_serializer_class = WriteOnlyTeachersSerializer
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            match self.request.user.user_type:
                case "T" | "SS":
                    return Teacher.objects.filter(
                        school=self.request.user.school)
                case "S":
                    return Teacher.objects.filter(
                        subject_teacher__class_subjects=self.request.user.student_user.student_class
                    ).distinct()


class UsersViewSet(_BaseViewSet):
    serializer_class = ReadOnlyUsersSerializer
    writeonly_serializer_class = WriteOnlyUsersSerializer
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            school = self.request.user.school
            teachers = get_user_model().objects.filter(
                teacher_user__school=school)
            principal = get_user_model().objects.filter(school_support=school)
            match self.request.user.user_type:
                case "T":
                    students = get_user_model().objects.filter(
                        student_user__student_class__subjects__teacher__school=school
                    ).distinct()
                    return teachers.union(students, principal)
                case "SS":
                    students = get_user_model().objects.filter(
                        student_user__student_class__school=school)
                    principal = get_user_model().objects.filter(
                        username=self.request.user.username)
                    return teachers | students | principal
                case "S":
                    student_class = self.request.user.student_user.student_class
                    teachers = get_user_model().objects.filter(
                        teacher_user__subject_teacher__in=student_class.subjects.all()
                    ).distinct()
                    students = get_user_model().objects.filter(
                        username=self.request.user.username)
                    return students.union(teachers, principal)
        return self.request.user.none()
    
    
class ClassesViewSet(_BaseViewSet):
    serializer_class = ReadOnlyClassesSerializer
    writeonly_serializer_class = WriteOnlyClassesSerializer
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            match self.request.user.user_type:
                case "T":
                    return Class.objects.filter(
                        subjects__teacher__user=self.request.user).distinct()
                case "SS":
                    return self.request.user.school_support.class_school.all()
                case "S":
                    return Class.objects.filter(student_class__user=self.request.user)
        return self.request.user.none()


class ExamsViewSet(_BaseViewSet):
    serializer_class = ReadOnlyExamsSerializer
    writeonly_serializer_class = WriteOnlyExamsSerializer
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            match self.request.user.user_type:
                case "T":
                    return Exam.objects.filter(
                        subject__teacher__user=self.request.user)
                case "SS":
                    return Exam.objects.filter(
                        exam_class__school=self.request.user.school)
                case "S":
                    return Exam.objects.filter(
                        exam_class=self.request.user.student_user.student_class)
        return self.request.user.none()


class ArticlesViewSet(_BaseViewSet):
    serializer_class = ReadOnlyArticlesSerializer
    writeonly_serializer_class = WriteOnlyArticlesSerializer
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Article.objects.filter(
                school=self.request.user.school)
        return Article.objects.none()
    

class AssignmentsViewSet(_BaseViewSet):
    serializer_class = ReadOnlyAssignmentsSerializer
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            user_type = self.request.user.user_type
            match user_type:
                case "SS":
                    return Assignment.objects.filter(
                        assignment_class__school=self.request.user.school)
                case "S":
                    return Assignment.objects.filter(
                        assignment_class=self.request.user.student_user.student_class)
                case "T":
                    return Assignment.objects.filter(
                        assignment_class__subjects__teacher__user=self.request.user
                    ).distinct()
                    
                    
class AssignmentsViewSet(_BaseViewSet):
    serializer_class = ReadOnlyAssignmentsSerializer
    writeonly_serializer_class = WriteOnlyAssignmentsSerializer
    
    def get_queryset(self):
        user = self.request.user
        user_type = user.user_type
        match user_type:
            case "SS":
                return Assignment.objects.filter(
                    assignment_class__school__support=user)
            case "S":
                student = Student.objects.filter(user=user)
                if student.exists():
                    student_class = student.first().student_class
                    return Assignment.objects.filter(assignment_class=student_class)
                return Assignment.objects.none()
            case "T":
                return Assignment.objects.filter(subject__teacher__user=user)


class GradesViewSet(_BaseViewSet):
    """A viewset for listing and creating."""
    writeonly_serializer_class = WriteOnlyGradesSerializer
    serializer_class = ReadOnlyGradesSerializer

    def get_queryset(self):
        user = self.request.user
        user_type = user.user_type
        match user_type:
            case "SS":
                return Grade.objects.filter(
                    exam__exam_class__school__support=user)
            case "T":
                return Grade.objects.filter(exam__teacher__user=user)
            case "S":
                return Grade.objects.filter(student__user=user)
