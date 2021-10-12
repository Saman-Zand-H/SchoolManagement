from django.db import models


class StudentManager(models.Manager):
    def grades(self):
        return self.model.grades.all()


class SubjectTeachers(models.Manager):
    def teachers(self):
        return self.model.teachers.all()


class ClassTeachers(models.Manager):
    def teachers(self):
        return self.model.teachers.all()


class ClassStudents(models.Manager):
    def teachers(self):
        return self.model.students.all()


class StudentClass(models.Manager):
    def get_classname(self):
        return self.get_queryset().filter(class_students__pk=self.pk)
