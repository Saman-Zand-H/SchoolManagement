from rest_framework.viewsets import  ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from .serializers import (StudentsSerializer, 
                          UsersSerializer, 
                          ClassesSerializer, 
                          ExamsSerializer,
                          ArticlesSerializer,
                          AssignmentsSerializer,
                          TeachersSerializer)
from .permissions import CanCreate
from mainapp.models import (Student, 
                            Class, 
                            Exam, 
                            Article, 
                            Assignment)
from teachers.models import Teacher


class StudentsViewSet(ReadOnlyModelViewSet):
    serializer_class = StudentsSerializer
    permission_classes = (CanCreate, IsAuthenticated)
    
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


class TeachersViewSet(ReadOnlyModelViewSet):
    permission = (CanCreate, IsAuthenticated)
    serializer_class = TeachersSerializer
    
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


class UsersViewSet(ReadOnlyModelViewSet):
    serializer_class = UsersSerializer
    permission_classes = (CanCreate, IsAuthenticated,)
    
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
    
    
class ClassesViewSet(ReadOnlyModelViewSet):
    serializer_class = ClassesSerializer
    permission_classes = (IsAuthenticated, CanCreate,)
    
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


class ExamsViewSet(ReadOnlyModelViewSet):
    serializer_class = ExamsSerializer
    permission_classes = (IsAuthenticated, CanCreate,)
    
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


class ArticlesViewSet(ReadOnlyModelViewSet):
    serializer_class = ArticlesSerializer
    permission_class = (IsAuthenticated, CanCreate,)
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Article.objects.filter(
                school=self.request.user.school)
        return Article.objects.none()
    

class AssignmentsViewSet(ReadOnlyModelViewSet):
    serializer_class = AssignmentsSerializer
    permission_class = (IsAuthenticated, CanCreate,)
    
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
