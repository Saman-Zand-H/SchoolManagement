from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model, get_user
from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from allauth.account.views import PasswordChangeView
from allauth.account.forms import ChangePasswordForm
from allauth.account.admin import EmailAddress

from collections import deque

from .forms import (CreateSchoolForm, CreateClassForm, ChangePhonenumber,
                    ChangeTeacherDetails, EditClassForm, CreateSubjectForm,
                    StudentsClassForm)
from mainapp.models import Class, Subject, Student
from .models import School
from teachers.models import Teacher
from users.forms import BaseSignupForm, SupportStudentSignupForm, UserBioForm
from mainapp.mixins import PermissionAndLoginRequiredMixin


class _BaseDeleteUser(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"

    def get(self, *args, **kwargs):
        user = get_user_model().objects.get(pk=kwargs.get("pk"))
        user.delete()


class CreateSchoolView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self, *args, **kwargs):
        return self.request.user.user_type == "SS"

    def get(self, *args, **kwargs):
        # Redirects to home if the user has a school already
        if not School.objects.filter(support=self.request.user).exists():
            form = CreateSchoolForm()
            return render(self.request, "account/register_school.html",
                          {"form": form})
        else:
            return redirect("home:home")

    def post(self, *args, **kwargs):
        if not School.objects.filter(support=self.request.user).exists():
            school_form = CreateSchoolForm(self.request.POST)
            if school_form.is_valid():
                school_form_uncommitted = school_form.save(commit=False)
                school_form_uncommitted.support = self.request.user
                school_form.save()
                messages.success(self.request,
                                 _("You registered successfully."))
                return redirect("home:home")
            else:
                messages.error(self.request, _("Provided inputs are invalid."))
                return render(self.request, "account/register_school.html",
                              {"form": school_form})
        else:
            return redirect("home:home")


create_school_view = CreateSchoolView.as_view()


class HomeView(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"

    def get(self, *args, **kwargs):
        school = School.objects.get(support=self.request.user)
        context = {
            "school": school,
            "classes": school.class_school.all()[:4],
            "teachers": school.teacher_school.all()[:4],
            "segment": "home"
        }
        return render(self.request, "dashboard/supports/index.html", context)


home_view = HomeView.as_view()


class ClassesView(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = dict()

    def get(self, *args, **kwargs):
        load_template = self.request.path.split("-1")[-1]
        school = School.objects.get(support=self.request.user)
        classes = Class.objects.filter(school=school).distinct()
        subjects_exist = Subject.objects.filter(
            teacher__school=school).exists()
        form = CreateClassForm(request=self.request)
        self.context = {
            "classes": classes,
            "form": form,
            "segment": load_template,
            "subjects_exist": subjects_exist
        }
        return render(self.request, "dashboard/supports/classes.html",
                      self.context)

    def post(self, *args, **kwargs):
        school = School.objects.get(support=self.request.user)
        form = CreateClassForm(request=self.request, data=self.request.POST)
        if form.is_valid():
            form.instance.school = school
            form.save()
            messages.success(self.request, _("Class saved successfully."))
            return redirect("supports:classes")
        else:
            self.context["form"] = form
            messages.error(self.request, _("Provided inputs are invalid."))
            return render(self.request, "dashboard/supports/classes.html",
                          self.context)


classes_view = ClassesView.as_view()


class ClassesDetailView(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"

    def get(self, *args, **kwargs):
        class_instance = Class.objects.get(pk=kwargs.get("pk"))
        form = EditClassForm(instance=class_instance, request=self.request)
        context = {
            "class": class_instance,
            "form": form,
        }
        return render(self.request, "dashboard/supports/classes_detail.html",
                      context)

    def post(self, *args, **kwargs):
        class_instance = Class.objects.get(pk=kwargs.get("pk"))
        form = EditClassForm(instance=class_instance,
                             request=self.request,
                             data=self.request.POST)
        if form.is_valid():
            chosen_subjects = form.cleaned_data.get("subjects")
            class_instance.subjects.remove(*class_instance.subjects.exclude(
                pk__in=chosen_subjects))
            form.save()
            messages.success(self.request, _("Class updated successfully."))
            return redirect("supports:classes-detail", pk=kwargs.get("pk"))
        else:
            context = {"form": form, "class": class_instance}
            messages.error(self.request, _("Provided inputs are invalid."))
            return render(self.request,
                          "dashboard/supports/classes_detail.html", context)


classes_detail_view = ClassesDetailView.as_view()


class DeleteClass(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"

    def get(self, *args, **kwargs):
        chosen_class = Class.objects.get(pk=kwargs.get("pk"))
        chosen_class.delete()
        messages.success(self.request, _("Class deleted successfully."))
        return redirect("supports:classes")


delete_class_view = DeleteClass.as_view()


class TeachersView(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = dict()

    def get(self, *args, **kwargs):
        load_template = self.request.path.split("-1")[-1]
        school = School.objects.get(support=self.request.user)
        teachers = Teacher.objects.filter(school=school).distinct()
        form = BaseSignupForm()
        self.context = {
            "teachers": teachers,
            "form": form,
            "segment": load_template
        }
        return render(self.request, "dashboard/supports/teachers.html",
                      self.context)

    def post(self, *args, **kwargs):
        form = BaseSignupForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            school = School.objects.get(support=self.request.user)
            user = form.save(self.request)
            Teacher.objects.create(user=user, school=school)
            messages.success(self.request, _("Teacher created successfully."))
            return redirect("supports:teachers")
        else:
            self.context["form"] = form
            messages.error(self.request, _("Provided inputs are invalid."))
            return render(self.request, "dashboard/supports/teachers.html",
                          self.context)


teachers_view = TeachersView.as_view()


class TeachersDetailView(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = dict()

    def get(self, *args, **kwargs):
        load_template = self.request.path.split("-1")[-1]
        teacher = Teacher.objects.get(pk=kwargs.get("pk"))
        subjects = teacher.subject_teacher.all()
        classes = Class.objects.filter(subjects__teacher=teacher).distinct()
        details_form = ChangeTeacherDetails(instance=teacher)
        change_number_form = ChangePhonenumber(instance=teacher.user)
        self.context = {
            "classes": classes,
            "teacher": teacher,
            "subjects": subjects,
            "details_form": details_form,
            "change_number_form": change_number_form,
            "segment": load_template,
        }
        return render(self.request, "dashboard/supports/teachers_detail.html",
                      self.context)

    def post(self, *args, **kwargs):
        teacher = Teacher.objects.get(pk=kwargs.get("pk"))
        details_form = ChangeTeacherDetails(instance=teacher,
                                            data=self.request.POST)
        phone_number_form = ChangePhonenumber(instance=teacher.user,
                                              data=self.request.POST)
        if details_form.is_valid() and phone_number_form.is_valid():
            deque(
                map(lambda forms: forms.save(),
                    [details_form, phone_number_form]))
            messages.success(self.request, _("Changes saved successfully."))
            return redirect("supports:teachers-detail", pk=kwargs.get("pk"))
        else:
            self.context["details_form"] = details_form
            self.context["phonenumber_form"] = phone_number_form
            messages.error(
                self.request,
                _("Invalid inputs detected. Consider that empty inputs are not allowed."
                  ))
            return render(self.request,
                          "dashboard/supports/teachers_detail.html",
                          self.context)


teachers_detail_view = TeachersDetailView.as_view()


class DeleteTeacher(_BaseDeleteUser):
    def get(self, *args, **kwargs):
        super().get(*args, **kwargs)
        messages.success(self.request, _("Teacher deleted successfully."))
        return redirect("supports:teachers")


delete_teacher_view = DeleteTeacher.as_view()


class SubjectsView(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = dict()

    def get(self, *args, **kwargs):
        load_template = self.request.path.split("-1")[-1]
        self.context = {
            "subjects":
            Subject.objects.filter(
                teacher__school__support=self.request.user).distinct(),
            "form":
            CreateSubjectForm(request=self.request),
            "segment":
            load_template,
        }
        return render(self.request, "dashboard/supports/subjects.html",
                      self.context)

    def post(self, *args, **kwargs):
        subject_form = CreateSubjectForm(request=self.request,
                                         data=self.request.POST)
        if subject_form.is_valid():
            subject_form.save()
            messages.success(self.request, _("Course created successfully."))
            return redirect("supports:subjects")
        else:
            self.context["subject_form"] = subject_form
            messages.error(self.request, _("Provided inputs are invalid."))
            return render(self.request, "dashboard/supports/subjects.html",
                          self.context)


subjects_view = SubjectsView.as_view()


class SubjectsDetailView(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"

    def get(self, *args, **kwargs):
        subject = Subject.objects.get(pk=kwargs["pk"])
        context = {
            "classes": subject.class_subjects.all(),
            "subject": subject,
        }
        return render(self.request, "dashboard/supports/subjects_detail.html",
                      context)


subjects_detail_view = SubjectsDetailView.as_view()


class DeleteSubject(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"

    def get(self, *args, **kwargs):
        subject = Subject.objects.get(pk=kwargs.get("pk"))
        subject.delete()
        messages.success(self.request, _("Course deleted successfully."))
        return redirect("supports:subjects")


delete_subject_view = DeleteSubject.as_view()


class StudentsView(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = dict()

    def get(self, *args, **kwargs):
        load_template = self.request.path.split("-1")[-1]
        students = Student.objects.filter(
            student_class__school__support=self.request.user).distinct()
        self.context = {
            "form": SupportStudentSignupForm(request=self.request),
            "students": students,
            "segment": load_template,
        }
        return render(self.request, "dashboard/supports/students.html",
                      self.context)

    def post(self, *args, **kwargs):
        form = SupportStudentSignupForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            chosen_class_id = form.cleaned_data.get("student_class").id
            chosen_class = Class.objects.get(pk=chosen_class_id)
            user = form.save(self.request)
            Student.objects.create(user=user, student_class=chosen_class)
            messages.success(self.request, _("Student created successfully."))
            return redirect("supports:students")
        else:
            self.context["form"] = form
            messages.error(self.request, _("Provided inputs are invalid."))
            return render(self.request, "dashboard/supports/students.html",
                          self.context)


students_view = StudentsView.as_view()


class StudentsDetailView(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"

    def get(self, *args, **kwargs):
        current_student = Student.objects.get(pk=kwargs.get("pk"))
        context = {
            "student_spec_form":
            StudentsClassForm(instance=current_student, request=self.request),
            "phonenumber_form":
            ChangePhonenumber(instance=current_student.user),
            "student":
            current_student,
        }
        return render(self.request, "dashboard/supports/students_detail.html",
                      context)

    def post(self, *args, **kwargs):
        current_student = Student.objects.get(pk=kwargs.get("pk"))
        student_spec_form = StudentsClassForm(instance=current_student,
                                              request=self.request,
                                              data=self.request.POST)
        phone_number_form = ChangePhonenumber(instance=current_student.user,
                                              data=self.request.POST)
        if phone_number_form.is_valid() and student_spec_form.is_valid():
            deque(
                map(lambda forms: forms.save(),
                    [student_spec_form, phone_number_form]))
            messages.success(self.request, _("Student updated successfully."))
            return redirect("supports:students-detail", pk=kwargs.get("pk"))
        else:
            context = {
                "student_spec_form": student_spec_form,
                "phonenumber_form": phone_number_form,
                "student": current_student,
            }
        return render(self.request, "dashboard/supports/students_detail.html",
                      context)


students_detail_view = StudentsDetailView.as_view()


class DeleteStudent(_BaseDeleteUser):
    def get(self, *args, **kwargs):
        super().get(*args, **kwargs)
        messages.success(self.request, _("Student deleted successfully."))
        return redirect("supports:students")


delete_student_view = DeleteStudent.as_view()


class ProfileView(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = dict()

    def get(self, args, **kwargs):
        # For some reason, that I don't know, [-1] is None
        load_template = self.request.path.split('/')[-2]
        classes = Class.objects.filter(
            school__support=self.request.user).distinct()
        students = Student.objects.filter(student_class__in=classes)
        email_confirmed = EmailAddress.objects.filter(
            user=self.request.user).distinct()
        self.context = {
            "form": ChangePasswordForm(),
            "classes_count": classes.count(),
            "students_count": students.count(),
            "segment": load_template,
        }
        if email_confirmed.exists():
            self.context["email_confirmed"] = email_confirmed[0].verified
        return render(self.request, "dashboard/supports/profile.html",
                      self.context)

    def post(self, *args, **kwargs):
        form = UserBioForm(self.request.POST)
        if form.is_valid():
            about = form.cleaned_data.get("about")
            user = get_user(self.request)
            user.about = about
            user.save()
            messages.success(self.request, _("Bio was updated successfully."))
            return redirect("supports:profile")
        else:
            messages.error(self.request, _("Provided inputs are invalid."))
            self.context["form"] = form
            return render(self.request, "dashboard/supports/profile.html",
                          self.context)


profile_view = ProfileView.as_view()


class CustomPasswordChangeView(PermissionAndLoginRequiredMixin,
                               PasswordChangeView):
    permission_required = "supports.support"
    template_name = "dashboard/supports/profile.html"
    success_url = reverse_lazy("supports:profile")

    def render_to_response(self, context, **response_kwargs):
        classes = Class.objects.filter(school__support=self.request.user)
        students = Student.objects.filter(student_class__in=classes).distinct()
        context["classes_count"] = classes.count()
        context["students_count"] = students.count()

        if not self.request.user.has_usable_password():
            return redirect("supports:profile")
        return super().render_to_response(context, **response_kwargs)


password_change_view = CustomPasswordChangeView.as_view()
