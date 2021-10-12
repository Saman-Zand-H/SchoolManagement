from django.test import TestCase
from django.contrib.auth import get_user_model

from mainapp.models import *


class ClassTests(TestCase):
    def setUp(self):
        self.student_user = get_user_model().objects.create_user("test_student", "s@test.com",
                                                            "test student", "123456789S@", "S")
        self.teacher_user = get_user_model().objects.create_user("test_teacher", "t@test.com",
                                                            "test teacher", "123456789S@", "T")
        self.student = Student.objects.get(user=self.student_user)
        self.teacher = Teacher.objects.get(user=self.teacher_user)

        self.subject = Subject.objects.create(subject="Math")
        self.subject.teachers.add(self.teacher)
        self.subject.save()

        self.exam = Exam.objects.create(teacher=self.teacher, subject=self.subject)

        self.test_class = Class.objects.create(class_id="901")

    def test_sets_up_properly(self):
        self.assertEqual(self.test_class.class_id, "901")
        self.assertNotEqual(self.test_class.class_id, "Oh no no no no no")
    
    def test_add_students(self):
        self.test_class.students.add(self.student)
        self.test_class.save()
        self.assertEqual(self.test_class.students.count(), 1)
        
    def test_add_teachers(self):
        self.test_class.teachers.add(self.teacher)
        self.test_class.save()
        self.assertEqual(self.test_class.teachers.count(), 1)

    def test_add_subjects(self):
        self.test_class.subjects.add(self.subject)
        self.test_class.save()
        self.assertEqual(self.test_class.subjects.count(), 1)
        self.assertEqual(self.test_class.subjects.first().subject, "Math")
        self.assertNotEqual(self.test_class.subjects.first().subject, "Arabic")

    def test_add_exam(self):
        self.test_class.exams.add(self.exam)
        self.test_class.save()
        self.assertEqual(self.test_class.exams.count(), 1)
        self.assertEqual(self.test_class.exams.first().subject, self.subject)


class ExamTest(TestCase):
    def setUp(self):
        self.student_user = get_user_model().objects.create_user("test_student", "s@test.com",
                                                                 "test student", "123456789S@", "S")
        self.teacher_user = get_user_model().objects.create_user("test_teacher", "t@test.com",
                                                                 "test teacher", "123456789S@", "T")
        self.student = Student.objects.get(user=self.student_user)
        self.teacher = Teacher.objects.get(user=self.teacher_user)

        self.subject = Subject.objects.create(subject="Math")
        self.subject.teachers.add(self.teacher)
        self.subject.save()

        self.grade = Grade.objects.create(student=self.student, subject=self.subject, grade=19.25)

        self.exam = Exam.objects.create(
            teacher=self.teacher, subject=self.subject)

    def test_sets_up_properly(self):
        self.assertEqual(self.exam.teachers.count(), 1)
        self.assertEqual(self.exam.teachers.first(), self.teacher)
        self.assertEqual(self.exam.subject.count(), 1)
        self.assertEqual(self.exam.subject.first(), self.subject)
        self.assertEqual(self.exam.grade, 19.25)

    def test_add_grade(self):
        self.exam.grades.add(self.grade)
        self.exam.save()
        self.assertEqual(self.exam.grades.count(), 1)
        self.assertEqual(self.exam.grades.first(), self.grade)