from rest_framework import serializers
from django.contrib.auth import  get_user_model

from mainapp.models import Student, Class, Exam, Grade, Article, Assignment
from supports.models import School
from teachers.models import Teacher


class UsersSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:users-detail")
    
    class Meta:
        model = get_user_model()
        fields = [
            "username", 
            "first_name", 
            "last_name", 
            "email", 
            "get_user_type_display",
            "url",
        ]
        
        
class StudentsSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:students-detail")
    user = UsersSerializer()
    student_class = serializers.StringRelatedField()

    class Meta:
        model = Student
        fields = ["user", "student_class", "url"]
        

class TeachersSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:teachers-detail")
    user = UsersSerializer()
    
    class Meta:
        model = Teacher
        fields = ["user", "url", "university", "degree"]


class ClassesSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:classes-detail")
    subjects = serializers.StringRelatedField(many=True)
    school = serializers.StringRelatedField()
    
    class Meta:
        model = Class
        exclude = ["id", ]
        
        
class GradesSerializers(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:grades-detail")
    student = serializers.StringRelatedField()
    exam = serializers.StringRelatedField()
    
    class Meta:
        model = Grade
        fields = ["grade", "student", "exam", "url"]


class ExamsSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:exams-detail")
    subject = serializers.StringRelatedField()
    teacher = serializers.StringRelatedField()
    exam_class = serializers.StringRelatedField()
    grade_exam = GradesSerializers(many=True)
    
    class Meta:
        model = Exam
        fields = [
            "url",
            "timestamp",
            "subject",
            "teacher",
            "exam_class",
            "grade_exam",
            "school",
        ]


class ArticlesSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:articles-detail")
    author = serializers.StringRelatedField()
    school = serializers.StringRelatedField()
    categories = serializers.ListField(child=serializers.CharField())
    
    class Meta:
        model = Article
        fields = [
            "title", 
            "author", 
            "school", 
            "url", 
            "categories", 
            "text", 
            "timestamp",
        ]


class AssignmentsSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:assignments-detail")
    assignment_class = serializers.StringRelatedField()
    subject = serializers.StringRelatedField()
    
    class Meta:
        model = Assignment
        fields = [
            "url",
            "assignment_class",
            "subject",
            "body",
            "deadline",
            "timestamp",
        ]
