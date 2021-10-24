from django.views.generic import View, TemplateView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from collections import deque

from .forms import (CreateSchoolForm,
                    CreateClassForm,
                    ChangePhonenumber,
                    ChangeTeacherDetails, 
                    EditClassForm,
                    SelectClassesForm,
                    CreateSubjectForm, StudentsClassForm)
from users.forms import SupportTeacherSignupForm, SupportStudentSignupForm
from mainapp.models import School, Class, Teacher, Subject, Student


class CreateSchoolView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.user_type == "SS"

    def get(self, *args, **kwargs):
        form = CreateSchoolForm()
        return render(self.request, "account/register_school.html",
                      {"form": form})

    def post(self, *args, **kwargs):
        form = CreateSchoolForm(self.request.POST)
        if form.is_valid():
            form.save()
            messages.success(self.request, "You registered successfully")
            return redirect("home:home")
        else:
            return render(self.request, "account/register_school.html",
                          {"form": form})


createschool_view = CreateSchoolView.as_view()


class HomeView(TemplateView):
    template_name = "dashboard/support/index.html"


class ClassesView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        school = School.objects.get(support=self.request.user)
        classes = Class.objects.filter(school=school)
        form = CreateClassForm(request=self.request)
        context = {"classes": classes, "form": form}
        return render(self.request, "dashboard/support/classes.html", context)

    def post(self, *args, **kwargs):
        school = School.objects.get(support=self.request.user)
        form = CreateClassForm(request=self.request, data=self.request.POST)
        if form.is_valid():
            form.instance.school = school
            form.save()
            messages.success(self.request, "Class created successfully")
            return redirect("support:classes")
        else:
            classes = Class.objects.filter(school=school)
            context = {"form": form, "classes": classes}
            messages.error(self.request, "Provided inputs are invalid.")
            return render(self.request, "dashboard/support/classes.html",
                          context)
classes_view = ClassesView.as_view()


class ClassesDetailView(View):
    def get(self, *args, **kwargs):
        class_instance = Class.objects.get(pk=kwargs.get("pk"))
        form = EditClassForm(instance=class_instance, request=self.request)
        context = {
            "class": class_instance,
            "form": form,
        }
        return render(self.request, "dashboard/support/classes_detail.html", context)

    def post(self, *args, **kwargs):
        class_instance = Class.objects.get(pk=kwargs.get("pk"))
        form = EditClassForm(instance=class_instance,
                             request=self.request, data=self.request.POST)
        if form.is_valid():
            chosen_subjects = form.cleaned_data.get("subjects")
            print(chosen_subjects)
            class_instance.subjects.remove(*class_instance.subjects.exclude(pk__in=chosen_subjects))
            form.save()
            messages.success(self.request, "Class created successfully")
            return redirect("support:classes-detail", pk=kwargs.get("pk"))
        else:
            context = {"form": form, "class": class_instance}
            messages.error(self.request, "Provided inputs are invalid.")
            return render(self.request, "dashboard/support/classes_detail.html",
                          context)
classes_detailview = ClassesDetailView.as_view()


class TeachersView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.user_type == "SS"

    def get(self, *args, **kwargs):
        school = School.objects.get(support=self.request.user)
        teachers = Teacher.objects.filter(school=school)
        form = SupportTeacherSignupForm(request=self.request)
        context = {"teachers": teachers, "form": form}
        return render(self.request, "dashboard/support/teachers.html", context)

    def post(self, *args, **kwargs):
        form = SupportTeacherSignupForm(self.request.POST,
                                        request=self.request)
        if form.is_valid():
            school = School.objects.get(support=self.request.user)
            user = form.save(self.request)
            Teacher.objects.create(user=user, school=school)
            messages.success(self.request, "Teacher created successfully")
            return redirect("support:teachers")
        else:
            school = School.objects.get(support=self.request.user)
            teachers = Teacher.objects.filter(school=school)
            context = {"form": form, "teachers": teachers}
            messages.error(self.request, "Provided inputs are invalid.")
            return render(self.request, "dashboard/support/teachers.html",
                          context)


teachers_view = TeachersView.as_view()


class TeachersDetailView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.user_type == "SS"

    def get(self, *args, **kwargs):
        teacher = Teacher.objects.get(pk=kwargs.get("pk"))
        subjects = teacher.subject_teacher.all()
        classes = Class.objects.filter(subjects__teacher=teacher)
        details_form = ChangeTeacherDetails(instance=teacher)
        phonenumber_form = ChangePhonenumber(instance=teacher.user)
        context = {
            "classes": classes,
            "teacher": teacher,
            "subjects": subjects,
            "details_form": details_form,
            "phonenumber_form": phonenumber_form,
        }
        return render(self.request, "dashboard/support/teachers_detail.html",
                      context)

    def post(self, *args, **kwargs):
        teacher = Teacher.objects.get(pk=kwargs.get("pk"))
        details_form = ChangeTeacherDetails(instance=teacher,
                                            data=self.request.POST)
        phonenumber_form = ChangePhonenumber(instance=teacher.user,
                                             data=self.request.POST)
        if details_form.is_valid() and phonenumber_form.is_valid():
            deque(
                map(lambda forms: forms.save(),
                    [details_form, phonenumber_form]))
            messages.success(self.request, "Your changes saved successfully.")
            return redirect("support:teachers-detail", pk=kwargs.get("pk"))
        else:
            messages.error(
                self.request,
                "Invalid input detected. Empty inputs are not allowed.")
            return redirect("support:teachers-detail", pk=kwargs.get("pk"))


teachers_detailview = TeachersDetailView.as_view()


class SubjectsView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.user_type == "SS"

    def get(self, *args, **kwargs):
        context = {
            "subjects":
            Subject.objects.filter(
                teacher__school__support=self.request.user),
            "form":
            CreateSubjectForm(request=self.request),
        }
        return render(self.request, "dashboard/support/subjects.html", context)

    def post(self, *args, **kwargs):
        subject_form = CreateSubjectForm(request=self.request, data=self.request.POST)
        if subject_form.is_valid():
            subject_form.save()
            messages.success(self.request, "Subject created successfully.")
            return redirect("support:subjects")
        else:
            context = {
                "subjects":
                Subject.objects.filter(
                    teacher__school__support=self.request.user),
                "form":
                subject_form,
            }
            messages.error(self.request, "Provided inputs are invalid.")
            return render(self.request, "dashboard/support/subjects.html",
                          context)
subjects_view = SubjectsView.as_view()


class SubjectsDetailView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        subject = Subject.objects.get(pk=kwargs["pk"])
        context = {
            "classes": subject.class_subjects.all(),
            "subject": subject,
        }
        return render(self.request, "dashboard/support/subjects_detail.html", context)
subjects_detailview = SubjectsDetailView.as_view()


class StudentsView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        students = Student.objects.filter(student_class__school__support=self.request.user)
        context = {
            "form": SupportStudentSignupForm(request=self.request),
            "students": students,
        }
        return render(self.request, "dashboard/support/students.html", context)

    def post(self, *args, **kwargs):
        form = SupportStudentSignupForm(self.request.POST,
                                        request=self.request)
        if form.is_valid():
            chosen_class_id = form.cleaned_data.get("student_class").id
            chosen_class = Class.objects.get(pk=chosen_class_id)
            user = form.save(self.request)
            Student.objects.create(user=user, student_class=chosen_class)
            messages.success(self.request, "Student created successfully")
            return redirect("support:students")
        else:
            students = Student.objects.filter(
                student_class__school__support=self.request.user)
            context = {
                "form": SupportStudentSignupForm(request=self.request),
                "students": students,
            }
            messages.error(self.request, "Provided inputs are invalid.")
            return render(self.request, "dashboard/support/students.html",
                          context)
students_view = StudentsView.as_view()


class StudentsDetailView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        current_student = Student.objects.get(pk=kwargs.get("pk"))
        context = {
            "student_spec_form": StudentsClassForm(instance=current_student, request=self.request),
            "phonenumber_form": ChangePhonenumber(instance=current_student.user),
            "student": current_student,
        }
        return render(self.request, "dashboard/support/students_detail.html", context)

    def post(self, *args, **kwargs):
        current_student = Student.objects.get(pk=kwargs.get("pk"))
        student_spec_form = StudentsClassForm(instance=current_student, request=self.request, data=self.request.POST)
        phonenumber_form = ChangePhonenumber(instance=current_student.user, data=self.request.POST)
        if phonenumber_form.is_valid() and student_spec_form.is_valid():
            deque(
                map(lambda forms: forms.save(),
                    [student_spec_form, phonenumber_form]))
            messages.success(self.request, "Student updated successfully.")
            return redirect("support:students-detail", pk=kwargs.get("pk"))
        else:
            context = {
                "student_spec_form": student_spec_form,
                "phonenumber_form": phonenumber_form,
                "student": current_student,
            }
        return render(self.request, "dashboard/support/students_detail.html", context)
students_detailview = StudentsDetailView.as_view()
