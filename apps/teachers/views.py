from django.shortcuts import render, redirect
from django.views.generic import View, DetailView, ListView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Q
from django.forms import modelformset_factory

from datetime import date

# TODO: IMPORTANT remove these idiot asterixes
from mainapp.models import *
from .forms import *
from mainapp.helpers import *


class DashboardView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        left_chart_time = date.today().month - 4
        right_chart_time = date.today().month - 3

        left_chart_months_numbers = [loop_through_month_number(
            left_chart_time + i)[0] for i in range(0, 8)]
        right_chart_months_numbers = [loop_through_month_number(
            right_chart_time + i)[0] for i in range(0, 6)]

        # The following lists are formatted in a way that can be used in the chart
        left_chart_months_names = [
            f'"{get_month_from_number(number)}"' for number in left_chart_months_numbers]
        right_chart_months_names = [
            f'"{get_month_from_number(number)}"' for number in right_chart_months_numbers]

        teacher = Teacher.objects.get(user=self.request.user)

        context = {
            "left_chart_labels": left_chart_months_names,
            "right_chart_labels": right_chart_months_names,
            "classes": Class.objects.filter(teachers=teacher),
            "teacher": teacher,
        }
        return render(self.request, "dashboard/index.html", context)
dashboardview = DashboardView.as_view()


class ClassesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        classes = Class.objects.filter(teachers__user=request.user)
        context = {
            "classes": classes,
        }
        return render(self.request, "dashboard/class.html", context)
classesview = ClassesView.as_view()


class ExamsListView(LoginRequiredMixin, ListView):
    model = Exam
    template_name = "dashboard/exams.html"
    context_object_name = "exams"

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        self.object_list = self.get_queryset()
        context = super(ExamsListView, self).get_context_data(
            *args, **kwargs)
        user = request.user
        exam = context["exams"].filter(
            teacher__user=request.user).order_by("timestamp")
        subjects = Subject.objects.filter(teachers__user=user)
        classes = Class.objects.filter(teachers__user=user)

        context["exams"] = exam
        context["subjects"] = subjects
        context["classes"] = classes
        form = FilterExamsForm(request.GET)

        if form.is_valid():
            exam = context["exams"].filter(
                teacher__user=request.user).order_by("timestamp")

            exams_since = form.cleaned_data.get("dateSince")
            exams_till = form.cleaned_data.get("dateTill")
            subject = form.cleaned_data.get("subjectFilter")
            exam_class = form.cleaned_data.get("classFilter")

            time_range_filter = filter_by_timestamp(exams_since, exams_till)
            subject_filter = Q(subject=subject)
            class_filter = Q(exam_class=exam_class)

            # This if statement is a way to filter by priority so that subject
            # is in higher priority.
            if time_range_filter:
                queryset = exam.filter(
                    time_range_filter & subject_filter & class_filter).order_by("timestamp")
            else:
                queryset = exam.filter(
                    subject_filter & class_filter).order_by("timestamp")
            context["filter"] = queryset

            return self.render_to_response(context=context)
examslistview = ExamsListView.as_view()


class CreateExamView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "mainapp.teacher_permission"

    def post(self, *args, **kwargs):
        form = ExamForm(self.request.POST)

        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            exam_class = form.cleaned_data.get('exam_class')
            full_score = form.cleaned_data.get('full_score')
            timestamp = form.cleaned_data.get('timestamp')

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
                class_instance.exams.add(exam_instance)
                class_instance.save()
                messages.success(self.request, "Exam created successfully")
                return redirect("teachers:exams")
            else:
                messages.warning(
                    self.request, "Only teachers can create exams")
                return redirect("teachers:dashboard")
createexamview = CreateExamView.as_view()


class DeleteExamView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "mainapp.teacher_permission"

    def post(self, *args, **kwargs):
        pk = kwargs["pk"]
        exam = Exam.objects.get(pk=pk)
        grades = exam.grades.all()

        if grades:
            map(exam.grades.remove, grades)
            grades.delete()
        exam.delete()

        messages.success(self.request, "Exam deleted successfully")
        return redirect("teachers:exams")
deleteexamview = DeleteExamView.as_view()


class SetGradesView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = "mainapp.teacher_permission"

    model = Exam
    template_name = "dashboard/grades.html"
    context_object_name = "exam"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam = context["exam"]
        context["grades"] = exam.grades.all().order_by("student")
        GradeFormset = modelformset_factory(Grade, form=SetGradeForm, max_num=exam.exam_class.students.count(
        ), extra=exam.exam_class.students.count())
        context['formset'] = GradeFormset(queryset=exam.grades.all())
        return context

    def post(self, request, **kwargs):
        pk = kwargs["pk"]
        exam = Exam.objects.get(pk=pk)
        GradeFormset = modelformset_factory(
            Grade, form=SetGradeForm, max_num=exam.exam_class.students.count())
        formset = GradeFormset(request.POST)
        
        if formset.is_valid():
            try:
                formset.save()
                for form in formset:
                    exam.grades.add(form.instance.pk)
                exam.save()
                return redirect("teachers:exams-detail", pk=exam.pk)
            except ValidationError:
                messages.error(self.request, "Grades cannot exceed the fullscore")
                return redirect("teachers:exams-detail", pk=exam.pk)
setgradesview = SetGradesView.as_view()


class ProfileView(LoginRequiredMixin, View):
    def get(self, args, **kwargs):
        teacher = Teacher.objects.get(user=self.request.user)
        context = {
            "teacher": teacher,
        }
        return render(self.request, "dashboard/profile.html", context)

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
