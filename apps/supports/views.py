from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.views.generic import View
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.utils.translation import gettext as _

from functools import partial
import logging

from .forms import (CreateSchoolForm, CreateClassForm, EditOperationType,
                    ChangeTeacherDetails, EditClassForm, CreateSubjectForm,
                    StudentsClassForm)
from mainapp.models import Class, Subject, Student
from .models import School
from teachers.models import Teacher
from users.forms import SupportSignupForm, SupportStudentSignupForm
from mainapp.mixins import PermissionAndLoginRequiredMixin

logger = logging.getLogger(__name__)


class CreateSchoolView(LoginRequiredMixin, View):
    template_name = "account/register_school.html"
    context = dict()
  
    def get(self, *args, **kwargs):
        if not School.objects.filter(support=self.request.user).exists():
            form = CreateSchoolForm()
            self.context["form"] = form
            messages.warning(self.request, _("You have to register your school first."))
            return render(self.request, self.template_name, self.context)
        return redirect("home:home")

    def post(self, *args, **kwargs):
        if not School.objects.filter(support=self.request.user).exists():
            form = CreateSchoolForm(self.request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                form.support = self.request.user
                form.save()
                messages.success(self.request,
                                 _("You registered successfully."))
                return redirect("home:home")
            self.context["form"] = form
            messages.error(self.request, _("Provided inputs are invalid."))
            return render(self.request, self.template_name, self.context)
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
    context = dict()
    template_name = "dashboard/supports/classes.html"

    def get(self, *args, **kwargs):
        load_template = self.request.path.split("/")
        try:
            school = School.objects.get(support=self.request.user)
            classes = Class.objects.filter(school=school).distinct()
            subjects_exist = Subject.objects.filter(
                teacher__school=school).exists()
            form = CreateClassForm(request=self.request)
            self.context.update({
                "classes": classes,
                "form": form,
                "segment": load_template,
                "subjects_exist": subjects_exist,
                "nav_color": "bg-gradient-yellow",
            })
            return render(self.request, self.template_name, self.context)
        except School.DoesNotExist:
            messages.error(self.request, _("You have to register your school first."))
            return redirect("supports:create_school")

    def post(self, *args, **kwargs):
        error_message = partial(messages.error, request=self.request)
        try:
            school = School.objects.get(support=self.request.user)
            form = CreateClassForm(request=self.request, data=self.request.POST)
            if form.is_valid():
                form.instance.school = school
                form.save()
                messages.success(self.request, _("Class saved successfully."))
                return redirect("supports:classes")
            else:
                self.context["form"] = form
                error_message(message=_("Provided inputs are invalid."))
                return render(self.request, self.template_name, self.context)
        except School.DoesNotExist:
            error_message(message=_("You have to register your school first."))
            return redirect("supports:create_school")


classes_view = ClassesView.as_view()


class ClassesDetailView(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"
    context = dict()
    template_name = "dashboard/supports/classes_detail.html"

    def get(self, *args, **kwargs):
        load_template = self.request.path.split("/")
        class_instance = get_object_or_404(Class, pk=kwargs.get("pk"))
        form = EditClassForm(instance=class_instance, request=self.request)
        self.context = {
            "class": class_instance,
            "form": form,
            "segment": load_template,
            "nav_color": "bg-gradient-yellow",
        }
        return render(self.request, self.template_name, self.context)

    def post(self, *args, **kwargs):
        operation_form = EditOperationType(self.request.POST)
        if operation_form.is_valid():
            operation = operation_form.cleaned_data.get("operation")
            class_instance = get_object_or_404(Class, pk=kwargs.get("pk"))
            match operation:
                case "uc":
                    form = EditClassForm(instance=class_instance,
                                        request=self.request,
                                        data=self.request.POST)
                    if form.is_valid():
                        chosen_subjects = form.cleaned_data.get("subjects")
                        class_instance.subjects.remove(*class_instance.subjects.exclude(
                        pk__in=chosen_subjects))
                        form.save()
                        messages.success(
                            self.request, _("Class updated successfully."))
                        return redirect("supports:classes-detail", pk=kwargs.get("pk"))
                    self.context.update({
                        "form": form, 
                        "class": class_instance,
                    })
                    messages.error(self.request, _("Provided inputs are invalid."))
                    return render(self.request, self.template_name, self.context)
                case "dc":
                    class_instance.delete()
                    messages.success(self.request, _("Class deleted successfully."))
                    return redirect("supports:classes")
            return redirect("supports:classes")
        messages.error(self.request, _("Provided inputs are invalid."))
        return redirect("supports:classes")


classes_detail_view = ClassesDetailView.as_view()


class TeachersView(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"
    template_name = "dashboard/supports/teachers.html"
    context = dict()

    def get(self, *args, **kwargs):
        load_template = self.request.path.split("/")
        school = get_object_or_404(School, support=self.request.user)
        teachers = Teacher.objects.filter(school=school).distinct()
        form = SupportSignupForm(self.request, initial={"user_type": "SS"})
        self.context.update({
            "teachers": teachers,
            "form": form,
            "segment": load_template,
            "nav_color": "bg-gradient-green"
        })
        return render(self.request, self.template_name, self.context)

    def post(self, *args, **kwargs):
        form = SupportSignupForm(self.request, self.request.POST, self.request.FILES)
        if form.is_valid():
            school = School.objects.get(support=self.request.user)
            user = form.save(self.request)
            Teacher.objects.create(user=user, school=school)
            messages.success(self.request, _("Teacher created successfully."))
            return redirect("supports:teachers")
        self.context["form"] = form
        logger.error(f"An error occurred while {self.request.user.username} was"
                     f" trying to create a teacher: {form.errors}")
        messages.error(self.request, _("Provided inputs are invalid."))
        return render(self.request, self.template_name, self.context)


teachers_view = TeachersView.as_view()


class TeachersDetailView(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"
    context = dict()
    template_name = "dashboard/supports/teachers_detail.html"

    def get(self, *args, **kwargs):
        load_template = self.request.path.split("/")
        teacher = get_object_or_404(Teacher, pk=kwargs.get("pk"))
        subjects = teacher.subject_teacher.all()
        classes = Class.objects.filter(
            subjects__teacher=teacher).distinct()
        details_form = ChangeTeacherDetails(instance=teacher)
        self.context.update({
            "classes": classes,
            "teacher": teacher,
            "subjects": subjects,
            "details_form": details_form,
            "segment": load_template,
            "nav_color": "bg-gradient-green",
        })
        return render(self.request, self.template_name, self.context)

    def post(self, *args, **kwargs):
        operation_form = EditOperationType(self.request.POST)
        error_message = partial(messages.error, request=self.request)
        success_message = partial(messages.success, request=self.request)
        if operation_form.is_valid():
            operation = operation_form.cleaned_data.get("operation")
            match operation:
                case "ut":
                    teacher = get_object_or_404(Teacher, pk=kwargs.get("pk"))
                    details_form = ChangeTeacherDetails(
                        instance=teacher, data=self.request.POST)
                    if details_form.is_valid():
                        details_form.save()
                        success_message(message=_("Changes saved successfully."))
                        return redirect(
                            "supports:teachers-detail", pk=kwargs.get("pk"))
                    logger.error(f"An error occurred while {self.request.user.username}"
                                  " was trying to edit teacher details: {details_form.errors}")
                    self.context["details_form"] = details_form
                    error_message(message=_("Invalid inputs detected. Consider"
                                            "that empty inputs are not allowed."
                    ))
                    return render(self.request, self.template_name, self.context)
                case "dt":
                    teacher = get_object_or_404(
                        Teacher, pk=kwargs.get("pk"))
                    teacher.user.delete()
                    success_message(message=_("Teacher deleted successfully."))
                    return redirect("supports:teachers")
        error_message(message=_("Provided inputs are invalid."))
        return redirect("supports:teachers")


teachers_detail_view = TeachersDetailView.as_view()


class SubjectsView(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"
    context = dict()
    template_name = "dashboard/supports/subjects.html"

    def get(self, *args, **kwargs):
        load_template = self.request.path.split("/")
        self.context.update({
            "subjects": Subject.objects.filter(
                teacher__school__support=self.request.user).distinct(),
            "form": CreateSubjectForm(request=self.request),
            "segment": load_template,
            "nav_color": "bg-gradient-dark"
        })
        return render(self.request, self.template_name, self.context)

    def post(self, *args, **kwargs):
        subject_form = CreateSubjectForm(request=self.request,
                                         data=self.request.POST)
        if subject_form.is_valid():
            subject_form.save()
            messages.success(self.request, _("Course created successfully."))
            return redirect("supports:subjects")
        self.context["subject_form"] = subject_form
        messages.error(self.request, _("Provided inputs are invalid."))
        return render(self.request, self.template_name, self.context)


subjects_view = SubjectsView.as_view()


class SubjectsDetailView(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"
    context = dict()
    template_name = "dashboard/supports/subjects_detail.html"

    def get(self, *args, **kwargs):
        load_template = self.request.path.split("/")
        subject = Subject.objects.get(pk=kwargs["pk"])
        self.context.update({
            "classes": subject.class_subjects.all(),
            "subject": subject,
            "segment": load_template,
            "nav_color": "bg-gradient-dark",
        })
        return render(self.request, self.template_name, self.context)
    
    def post(self, *args, **kwargs):
        operation_form = EditOperationType(self.request.POST)
        if operation_form.is_valid():
            operation_type = operation_form.cleaned_data.get("operation")
            match operation_type:
                case "dc":
                    subject = Subject.objects.get(pk=kwargs.get("pk"))
                    subject.delete()
                    messages.success(self.request, _("Course deleted successfully."))
                    return redirect("supports:subjects")
        messages.error(self.request, _("Provided inputs are invalid."))
        return redirect("supports:subjects")

subjects_detail_view = SubjectsDetailView.as_view()


class StudentsView(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"
    context = dict()
    template_name = "dashboard/supports/students.html"

    def get(self, *args, **kwargs):
        load_template = self.request.path.split("/")
        students = Student.objects.filter(
            student_class__school__support=self.request.user).distinct()
        self.context = {
            "form": SupportStudentSignupForm(request=self.request),
            "students": students,
            "segment": load_template,
            "nav_color": "bg-gradient-default"
        }
        return render(self.request, self.template_name, self.context)

    def post(self, *args, **kwargs):
        form = SupportStudentSignupForm(data=self.request.POST, 
                                        files=self.request.FILES, 
                                        request=self.request)
        if form.is_valid():
            chosen_class_id = form.cleaned_data.get("student_class").id
            chosen_class = get_object_or_404(Class, pk=chosen_class_id)
            user = form.save(self.request)
            Student.objects.create(user=user, student_class=chosen_class)
            messages.success(self.request, _("Student created successfully."))
            return redirect("supports:students")
        self.context["form"] = form
        logger.error(f"An error occured when user {self.request.user.username}"
                     f" tried to sign up a student: {form.errors}")
        messages.error(self.request, _("Provided inputs are invalid."))
        return render(self.request, self.template_name, self.context)


students_view = StudentsView.as_view()


class StudentsDetailView(PermissionAndLoginRequiredMixin, View):
    permission_required = "supports.support"
    context = dict()
    template_name = "dashboard/supports/students_detail.html"

    def get(self, *args, **kwargs):
        load_template = self.request.path.split("/")
        current_student = Student.objects.get(pk=kwargs.get("pk"))
        self.context.update({
            "student_spec_form": StudentsClassForm(
                instance=current_student, request=self.request),
            "student": current_student,
            "segment": load_template,
            "nav_color": "bg-gradient-default"
        })
        return render(self.request, self.template_name, self.context)

    def post(self, *args, **kwargs):
        operation_form = EditOperationType(self.request.POST)
        if operation_form.is_valid():
            operation_type = operation_form.cleaned_data.get("operation")
            match operation_type:
                case "us":
                        current_student = get_object_or_404(Student, pk=kwargs.get("pk"))
                        student_spec_form = StudentsClassForm(instance=current_student,
                                                            request=self.request,
                                                            data=self.request.POST)
                        if student_spec_form.is_valid():
                            student_spec_form.save()
                            messages.success(self.request, _("Student updated successfully."))
                            return redirect("supports:students-detail", pk=kwargs.get("pk"))
                        self.context.update({
                            "student_spec_form": student_spec_form,
                            "student": current_student,
                        })
                        return render(self.request, self.template_name, self.context)
                case "ds":
                    get_object_or_404(get_user_model(), pk=kwargs.get("pk")).delete()
                    messages.success(self.request, _("Student deleted successfully."))
                    return redirect("supports:students")
        messages.error(self.request, _("Provided inputs are invalid."))
        return redirect("supports:students-detail", pk=kwargs.get("pk"))


students_detail_view = StudentsDetailView.as_view()
