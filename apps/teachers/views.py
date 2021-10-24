from django.shortcuts import render, redirect
from django.views.generic import View, DetailView, ListView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Q
from django.forms import modelformset_factory

from datetime import date
from typing import List

from mainapp.models import (Class,
                            Teacher,
                            Exam,
                            Grade,
                            Subject,
                            Student)
from .forms import (ExamForm,
                    FilterExamsForm,
                    SetGradeForm,
                    SetUserBiographyForm)
from mainapp.helpers import (loop_through_month_number, 
                             filter_by_timestamp, 
                             get_month_from_number)


def get_charts_labels_ready(eight_months_initial: int = 4, six_months_initial: int = 3) -> List:
    # Evaluate the performance, beginning from 3 and 4 months ago
    left_chart_time = date.today().month - eight_months_initial
    right_chart_time = date.today().month - six_months_initial

    # Make a list that consists of the month numbers
    eight_months_chart_month_numbers = [
        loop_through_month_number(left_chart_time + i)[0]
        for i in range(0, 8)
    ]
    six_months_chart_month_numbers = [
        loop_through_month_number(right_chart_time + i)[0]
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

class DashboardView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        teacher = Teacher.objects.get(user=self.request.user)
        class_instances = Class.objects.filter(subjects__teacher=teacher)

        context = {
            "eight_months_chart_labels": get_charts_labels_ready()[0],
            "six_months_chart_labels": get_charts_labels_ready()[1],
            "classes": class_instances,
            "teacher": teacher,
        }
        return render(self.request, "dashboard/teachers/index.html", context)
dashboardview = DashboardView.as_view()


class ClassesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        classes = Class.objects.filter(subjects__teacher__user=request.user)
        context = {
            "classes": classes,
        }
        return render(self.request, "dashboard/teachers/class.html", context)


classesview = ClassesView.as_view()


class ExamsListView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        current_teacher = Teacher.objects.get(user=self.request.user)
        exams = current_teacher.exam_teacher.all().order_by("timestamp")
        classes = Class.objects.filter(subjects__teacher=current_teacher)

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

            time_range_filter = filter_by_timestamp(exams_since, exams_till) or ~Q(pk__in=[])
            subject_filter = Q(subject=subject) if subject is not None else ~Q(pk__in=[])
            class_filter = Q(exam_class=exam_class) if exam_class is not None else ~Q(pk__in=[])

            queryset = exams.filter(time_range_filter & subject_filter & class_filter).order_by("timestamp")
            context["exams"] = queryset
        else:
            messages.error(self.request, "Provided inputs are invalid.")
        return render(self.request, "dashboard/teachers/exams.html", context)
    
    def post(self, *args, **kwargs):
        form = ExamForm(self.request.POST)

        if form.is_valid():
            subject = form.cleaned_data.get("subject")
            exam_class = form.cleaned_data.get("exam_class")

            full_score_cleaned = form.cleaned_data.get("full_score")
            if full_score_cleaned is not None:
                full_score = full_score_cleaned
            else:
                full_score = 20.0
            timestamp = form.cleaned_data.get("timestamp")

            subject_instance = Subject.objects.get(pk=subject)
            class_instance = Class.objects.get(pk=exam_class)

            teacher = Teacher.objects.filter(user=self.request.user)

            if teacher.exists():
                exam_instance = Exam.objects.create(
                    subject=subject_instance,
                    exam_class=class_instance,
                    full_score=full_score,
                    timestamp=timestamp,
                    teacher=teacher[0],
                )
                messages.success(self.request, "Exam created successfully")
                return redirect("teachers:exams")
            else:
                messages.warning(self.request,
                                 "Only teachers can create exams")
                return redirect("teachers:home")
examslistview = ExamsListView.as_view()


def ajax_create_exam(request):
    class_pk = request.GET.get("ajax_exam_class")
    if class_pk is not None:
        class_instance = Class.objects.get(pk=class_pk)
        print(class_instance)
        subjects = class_instance.subjects.filter(teacher__user=request.user)
    else:
        subjects = Subject.objects.none()
    context = {"subjects": subjects}
    return render(request, "dashboard/teachers/ajax-pages/exams-form.html", context)


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


class DeleteExamView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "mainapp.teacher_permission"

    def get(self, *args, **kwargs):
        pk = kwargs["pk"]

        exam = Exam.objects.get(pk=pk)
        grades = Grade.objects.filter(exam=exam)

        grades.delete()
        exam.delete()

        messages.success(self.request, "Exam deleted successfully")
        return redirect("teachers:exams")


deleteexamview = DeleteExamView.as_view()


class SetGradesView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = "mainapp.teacher_permission"

    model = Exam
    template_name = "dashboard/teachers/grades.html"
    context_object_name = "exam"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam = context["exam"]
        context["grades"] = exam.grade_exam.all().order_by("student")
        if exam.grade_exam.all():
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
        context["formset"] = GradeFormset(queryset=exam.grade_exam.all())
        return context

    def post(self, request, **kwargs):
        pk = kwargs["pk"]
        exam = Exam.objects.get(pk=pk)
        GradeFormset = modelformset_factory(
            Grade,
            form=SetGradeForm,
            max_num=exam.exam_class.student_class.count())
        formset = GradeFormset(request.POST)

        if formset.is_valid():
            try:
                formset.save()
                messages.success(self.request, "Grades submitted successfully")
                return redirect("teachers:exams-detail", pk=exam.pk)
            except ValidationError:
                messages.error(self.request,
                               "Grades cannot exceed the full score")
                return redirect("teachers:exams-detail", pk=exam.pk)


setgradesview = SetGradesView.as_view()


class ProfileView(LoginRequiredMixin, View):
    def get(self, args, **kwargs):
        teacher = Teacher.objects.get(user=self.request.user)
        context = {
            "teacher": teacher,
        }
        return render(self.request, "dashboard/teachers/profile.html", context)

    def post(self, *args, **kwargs):
        form = SetUserBiographyForm(self.request.POST)

        if form.is_valid():
            about = form.cleaned_data.get("about")

            user = get_user_model().objects.get(pk=self.request.user.pk)
            user.about = about
            user.save()

            messages.success(self.request, "About Me updated successfully")
            return redirect("teachers:profile")


profileview = ProfileView.as_view()


class StudentsView(View):
    def get(self, *args, **kwargs):
        students = Student.objects.filter(student_class__subjects__teacher__user=self.request.user)
        return render(self.request, "dashboard/teachers/students.html", {"students": students})
students_view = StudentsView.as_view()