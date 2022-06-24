from rest_framework import serializers
from django.contrib.auth import get_user_model

from mainapp.models import (Student, 
                            Class, 
                            Exam, 
                            Grade, 
                            Article, 
                            Assignment,
                            Subject)
from supports.models import School
from teachers.models import Teacher


class ReadOnlyUsersSerializer(serializers.ModelSerializer):
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
        

class WriteOnlyUsersSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "user_type",
            "about",
        ]    
    
    def create(self, validated_data):
        user = get_user_model().objects.create(
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data.get("email"),
            password=validated_data["password"],
            user_type=validated_data["user_type"],
            about=validated_data.get("about"),
        )
        return user


class ReadOnlyStudentsSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:students-detail")
    user = ReadOnlyUsersSerializer()
    student_class = serializers.StringRelatedField()

    class Meta:
        model = Student
        fields = ["user", "student_class", "url"]
        
        
class WriteOnlyStudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        exclude = ["id"]


class ReadOnlyTeachersSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:teachers-detail")
    user = ReadOnlyUsersSerializer()

    class Meta:
        model = Teacher
        fields = ["user", "url", "university", "degree"]


class WriteOnlyTeachersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        exclude = ["id"]


class ReadOnlyClassesSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:classes-detail")
    subjects = serializers.StringRelatedField(many=True)
    school = serializers.StringRelatedField()

    class Meta:
        model = Class
        exclude = [
            "id",
        ]
        
        
class WriteOnlyClassesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        exclude = ["id"]


class ReadOnlyGradesSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:grades-detail")
    student = serializers.StringRelatedField()

    class Meta:
        model = Grade
        fields = ["grade", "student", "exam", "url"]
        
        
class WriteOnlyGradesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        exclude = ["id"]


class ReadOnlyExamsSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:exams-detail")
    subject = serializers.StringRelatedField()
    teacher = serializers.StringRelatedField()
    exam_class = serializers.StringRelatedField()
    grade_exam = ReadOnlyGradesSerializer(many=True)

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


class WriteOnlyExamsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        exclude = ["id"]


class ReadOnlyArticlesSerializer(serializers.ModelSerializer):
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
        
        
class WriteOnlyArticlesSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all(), 
                                                required=True)
    school = serializers.PrimaryKeyRelatedField(queryset=School.objects.all(),
                                                required=True)
    class Meta:
        model = Article
        exclude = ["timestamp", "id"]


class ReadOnlyAssignmentsSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="api:assignments-detail")
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


class WriteOnlyAssignmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        exclude = ["timestamp", "id"]
