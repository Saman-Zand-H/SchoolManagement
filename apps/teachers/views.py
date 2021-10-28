from django.shortcuts import render, redirect
from django.views.generic import View, DetailView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user_model, get_user
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Q
from django.forms import modelformset_factory

from datetime import date
from typing import List

from mainapp.models import (Class, Teacher, Exam, Grade, Subject, Student)
from .forms import (ExamForm, FilterExamsForm, SetGradeForm,
                    SetUserBiographyForm)
from mainapp.helpers import (loop_through_month_number, filter_by_timestamp,
                             get_month_from_number)
from mainapp.mixins import PermissionAndLoginRequiredMixin


def get_charts_labels_ready() -> List:
    """
    Evaluates and formats labels so that they are feasible to be used by the charts.
    """
    eight_months_chart_time = date.today().month - 4
    six_months_chart_time = date.today().month - 3

    # Make a list that consists of the month numbers
    eight_months_chart_month_numbers = [
        loop_through_month_number(eight_months_chart_time + i)[1] for i in range(0, 8)
    ]
    six_months_chart_month_numbers = [
        loop_through_month_number(six_months_chart_time + i)[1]
        for i in range(0, 6)
    ]

    # The following lists are formatted in a way that can be used in the chart
    eight_months_chart_month_names = [
        f'"{get_month_from_number(number)}"'
        for number in eight_months_chart_month_numbers
    ]
    six_months_chart_month_names = [
        f'"{get_month_from_number(number)}"'
        for number in six_months_chart_month_numbers
    ]
    return [eight_months_chart_month_names, six_months_chart_month_names]


class DashboardView(PermissionAndLoginRequiredMixin, View):
    permission_required = "mainapp.teacher"

    def get(self, *args, **kwargs):
        teacher = Teacher.objects.get(user=self.request.user)
        class_instances = Class.objects.filter(
            subjects__teacher=teacher).distinct()

        context = {
            "eight_months_chart_labels": get_charts_labels_ready()[0],
            "six_months_chart_labels": get_charts_labels_ready()[1],
            "classes": class_instances,
            "teacher": teacher,
        }
        return render(self.request, "dashboard/teachers/index.html", context)
dashboardview = DashboardView.as_view()


class ClassesView(PermissionAndLoginRequiredMixin, View):
    permission_required = "mainapp.teacher"

    def get(self, request, *args, **kwargs):
        classes = Class.objects.filter(
            subjects__teacher__user=request.user).distinct()
        context = {
            "classes": classes,
        }
        return render(self.request, "dashboard/teachers/classes.html", context)
classesview = ClassesView.as_view()


class ExamsListView(PermissionAndLoginRequiredMixin, View):
    permission_required = "mainapp.teacher"

    def get(self, *args, **kwargs):
        current_teacher = Teacher.objects.get(user=self.request.user)
        exams = current_teacher.exam_teacher.all().order_by("timestamp")
        classes = Class.objects.filter(
            subjects__teacher=current_teacher).distinct()
        context = {
            "classes": classes,
            "exams": exams,
        }

        # Handle filters
        form = FilterExamsForm(self.request.GET)
        if form.is_valid():
            exams_since = form.cleaned_data.get("dateSince")
            exams_till = form.cleaned_data.get("dateTill")
            subject = form.cleaned_data.get("subjectFilter")
            exam_class = form.cleaned_data.get("classFilter")

            time_range_filter = filter_by_timestamp(
                exams_since, exams_till) or ~Q(pk__in=[])
            subject_filter = Q(
                subject=subject) if subject is not None else ~Q(pk__in=[])
            class_filter = Q(
                exam_class=exam_class) if exam_class is not None else ~Q(
                    pk__in=[])

            queryset = exams.filter(time_range_filter & subject_filter
                                    & class_filter).order_by("timestamp")
            context["exams"] = queryset
        else:
            messages.error(self.request, "Provided inputs are invalid.")
        return render(self.request, "dashboard/teachers/exams.html", context)

    def post(self, *args, **kwargs):
        form = ExamForm(self.request.POST)

        if form.is_valid():
            cleaned_subject = form.cleaned_data.get("subject")
            cleaned_exam_class = form.cleaned_data.get("exam_class")
            cleaned_full_score = form.cleaned_data.get("full_score")
            timestamp = form.cleaned_data.get("timestamp")

            full_score = cleaned_full_score or 20.0
            chosen_subject_instance = Subject.objects.get(pk=cleaned_subject)
            chosen_class_instance = Class.objects.get(pk=cleaned_exam_class)
            teacher = Teacher.objects.get(user=self.request.user)

            Exam.objects.create(subject=chosen_subject_instance,
                                exam_class=chosen_class_instance,
                                full_score=full_score,
                                timestamp=timestamp,
                                teacher=teacher)
            messages.success(self.request, "Exam created successfully.")
            return redirect("teachers:exams")
examslistview = ExamsListView.as_view()


@login_required
@permission_required("mainapp.teacher")
def ajax_create_exam(request):
    class_pk = request.GET.get("ajax_exam_class")
    if class_pk is not None:
        class_instance = Class.objects.get(pk=class_pk)
        print(class_instance)
        subjects = class_instance.subjects.filter(teacher__user=request.user)
    else:
        subjects = Subject.objects.none()
    context = {"subjects": subjects}
    return render(request, "dashboard/teachers/ajax-pages/exams-form.html",
                  context)


@login_required
@permission_required("mainapp.teacher")
def ajax_filter_exam(request):
    class_pk = request.GET.get("classFilter")
    if class_pk is not None:
        class_instance = Class.objects.get(pk=class_pk)
        subjects = class_instance.subjects.all()
    else:
        subjects = Subject.objects.none()
    context = {"subjects": subjects}
    return render(request, "dashboard/teachers/ajax-pages/exams-filter.html",
                  context)


class DeleteExamView(PermissionAndLoginRequiredMixin, View):
    permission_required = "mainapp.teacher"

    def get(self, *args, **kwargs):
        pk = kwargs["pk"]
        exam = Exam.objects.get(pk=pk)
        grades = Grade.objects.filter(exam=exam)
        grades.delete()
        exam.delete()
        messages.success(self.request, "Exam is deleted successfully.")
        return redirect("teachers:exams")
deleteexamview = DeleteExamView.as_view()


class SetGradesView(PermissionAndLoginRequiredMixin, View):
    permission_required = "mainapp.teacher"

    def get(self, *args, **kwargs):
        exam = Exam.objects.get(pk=kwargs["pk"])
        grades = exam.grade_exam.all().order_by("student")
        if exam.grade_exam.count() > 0:
            GradeFormset = modelformset_factory(
                Grade,
                form=SetGradeForm,
                max_num=exam.exam_class.student_class.count())
        else:
            GradeFormset = modelformset_factory(
                Grade,
                form=SetGradeForm,
                extra=exam.exam_class.student_class.count(),
                max_num=exam.exam_class.student_class.count(),
            )
        formset = GradeFormset(queryset=exam.grade_exam.all())
        context = {"exam": exam, "grades": grades, "formset": formset}
        return render(self.request, "dashboard/teachers/grades.html", context)

    def post(self, *args, **kwargs):
        pk = kwargs["pk"]
        exam = Exam.objects.get(pk=pk)
        GradeFormset = modelformset_factory(
            Grade,
            form=SetGradeForm,
            max_num=exam.exam_class.student_class.count())
        formset = GradeFormset(self.request.POST)
        if formset.is_valid():
            try:
                formset.save()
                messages.success(self.request, "Grades submitted successfully.")
                return redirect("teachers:exams-detail", pk=exam.pk)
            except ValidationError:
                messages.error(self.request, "Grades cannot exceed the full score.")
                return redirect("teachers:exams-detail", pk=exam.pk)
        else:
            grades = exam.grade_exam.all().order_by("student")
            context = {"exam": exam, "grades": grades, "formset": formset}
            messages.error(self.request, "Provided inputs are invalid.")
            return render(self.request, "dashboard/teachers/grades.html", context)
setgradesview = SetGradesView.as_view()


class ProfileView(PermissionAndLoginRequiredMixin, View):
    permission_required = "mainapp.teacher"

    def get(self, args, **kwargs):
        teacher = Teacher.objects.get(user=self.request.user)
        return render(self.request, "dashboard/teachers/profile.html",
                      {"teacher": teacher})

    def post(self, *args, **kwargs):
        form = SetUserBiographyForm(self.request.POST)
        if form.is_valid():
            about = form.cleaned_data.get("about")
            user = get_user(self.request)
            user.about = about
            user.save()
            messages.success(self.request, "User bio updated successfully.")
            return redirect("teachers:profile")
        else:
            messages.error(self.request, "Provided inputs are invalid.")
            return redirect("teachers:profile")
profileview = ProfileView.as_view()


class StudentsView(PermissionAndLoginRequiredMixin, View):
    permission_required = "mainapp.teacher"

    def get(self, *args, **kwargs):
        students = Student.objects.filter(
            student_class__subjects__teacher__user=self.request.user).distinct(
            )
        return render(self.request, "dashboard/teachers/students.html",
                      {"students": students})
students_view = StudentsView.as_view()


class StudentsDetailView(PermissionAndLoginRequiredMixin, DetailView):
    permission_required = "mainapp.teacher"
    template_name = "dashboard/teachers/students_detail.html"
    model = Student
students_detailview = StudentsDetailView.as_view()
