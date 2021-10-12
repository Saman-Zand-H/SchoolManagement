from django.test import TestCase
from django.contrib.auth import get_user_model

from mainapp.models import Student, Teacher


class UserModelTests(TestCase):
    def setUp(self):
        self.user_std = get_user_model().objects.create_user("test", "test@tset.com", 
                                                         "test user", "123456789s", "S")
        self.user_tch = get_user_model().objects.create_user("test_tch", "test@tshkjhet.com", 
                                                         "test teacher", "123456789s", "T")
    
    def test_user_custom_attrs(self):
        self.assertEqual(self.user_std.name, "test user")
        self.assertEqual(self.user_std.user_id, "test")
        self.assertEqual(self.user_std.user_type, "S")

        self.assertEqual(self.user_tch.name, "test teacher")
        self.assertEqual(self.user_tch.user_id, "test_tch")
        self.assertEqual(self.user_tch.user_type, "T")

    def test_signals(self):
        student = Student.objects.filter(user=self.user_std)
        teacher = Teacher.objects.filter(user=self.user_tch)

        self.assertEqual(student.exists(), True)
        self.assertEqual(teacher.exists(), True)
