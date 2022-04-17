from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, DetailView, TemplateView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.forms import modelformset_factory
from django.utils.translation import gettext as _

from datetime import date
from dateutil.relativedelta import relativedelta
from functools import partial
from logging import getLogger

from mainapp.models import Class, Exam, Grade, Subject, Student
from .forms import ExamForm, SetGradeForm, OperationType
from .filters import ExamFilter
from mainapp.mixins import PermissionAndLoginRequiredMixin
from .models import Teacher


logger = getLogger(__name__)


def get_charts_labels_ready():
    eight_months_chart_time = date.today() - relativedelta(months=4)
    six_months_chart_time = date.today() - relativedelta(months=3)
    eight_months_chart_months = [
        eight_months_chart_time + relativedelta(months=i) for i in range(8)]
    six_months_chart_months = [
        six_months_chart_time + relativedelta(months=i) for i in range(6)]
    # The way the names are formatted lets chart.js recognize the values
    eight_months_chart_month_names = [
        f'"{month.strftime("%b")}"' for month in eight_months_chart_months]
    six_months_chart_month_names = [
        f'"{month.strftime("%b")}"' for month in six_months_chart_months]
    return [eight_months_chart_month_names, six_months_chart_month_names]


class DashboardView(PermissionAndLoginRequiredMixin, View):
    permission_required = "teachers.teacher"

    def get(self, *args, **kwargs):
        teacher = Teacher.objects.get(user=self.request.user)
        class_instances = Class.objects.filter(
            subjects__teacher=teacher).distinct()
        labels = get_charts_labels_ready()
        context = {
            "eight_months_chart_labels": labels[0],
            "six_months_chart_labels": labels[1],
            "classes": class_instances,
            "teacher": teacher,
            "segment": "home",
        }
        return render(self.request, "dashboard/teachers/index.html", context)


dashboard_view = DashboardView.as_view()


class ClassesView(PermissionAndLoginRequiredMixin, View):
    permission_required = "teachers.teacher"

    def get(self, request, *args, **kwargs):
        loadTemplate = self.request.path.split('/')
        classes = Class.objects.filter(
            subjects__teacher__user=request.user).distinct()
        context = {
            "classes": classes,
            "segment": loadTemplate,
            "nav_color": "bg-gradient-yellow",
        }
        return render(self.request, "dashboard/teachers/classes.html", context)


classes_view = ClassesView.as_view()


class ExamsListView(PermissionAndLoginRequiredMixin, View):
    permission_required = "teachers.teacher"
    context = dict()
    template_name = "dashboard/teachers/exams.html"    

    def get(self, *args, **kwargs):
        loadTemplate = self.request.path.split('/')
        current_teacher = get_object_or_404(Teacher, user=self.request.user)
        exams = current_teacher.exam_teacher.all().order_by("timestamp")
        classes = Class.objects.filter(
            subjects__teacher=current_teacher).distinct()
        filters_form = ExamFilter(self.request.GET, queryset=exams)
        self.context = {
            "classes": classes,
            "exams": exams,
            "segment": loadTemplate,
            "filter": filters_form,
            "nav_color": "bg-gradient-default",
        }
        return render(self.request,  self.template_name, self.context)

    def post(self, *args, **kwargs):
        form = ExamForm(self.request.POST)

        if form.is_valid():
            subject = form.cleaned_data.get("subject")
            exam_class = form.cleaned_data.get("exam_class")
            full_score = form.cleaned_data.get("full_score", 20.0)
            timestamp = form.cleaned_data.get("timestamp")
            chosen_subject_instance = get_object_or_404(Subject, pk=subject)
            chosen_class_instance = get_object_or_404(Class, pk=exam_class)
            teacher = get_object_or_404(Teacher, user=self.request.user)
            Exam.objects.create(subject=chosen_subject_instance,
                                exam_class=chosen_class_instance,
                                full_score=full_score,
                                timestamp=timestamp,
                                teacher=teacher)
            messages.success(self.request, _("Exam created successfully."))
            return redirect("teachers:exams")
        else:
            messages.error(self.request, _("Provided inputs are invalid."))
            self.context.update({"form": form})
            return render(self.request, "dashboard/teachers/exams.html",
                          self.context)


exams_list_view = ExamsListView.as_view()


@login_required
@permission_required("teachers.teacher")
def ajax_create_exam(request):
    class_pk = request.GET.get("ajax_exam_class")
    if class_pk is not None:
        class_instance = Class.objects.get(pk=class_pk)
        subjects = class_instance.subjects.filter(
            teacher__user=request.user).distinct()
    else:
        subjects = Subject.objects.none()
    context = {"subjects": subjects}
    return render(request, "dashboard/teachers/ajax-pages/exams-form.html",
                  context)


class ExamDetailView(PermissionAndLoginRequiredMixin, View):
    permission_required = "teachers.teacher"

    def get(self, *args, **kwargs):
        loadTemplate = self.request.path.split("/")
        exam = Exam.objects.get(pk=kwargs["pk"])
        grades = exam.grade_exam.all().order_by("student")
        if exam.grade_exam.exists():
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
        context = {
            "exam": exam,
            "grades": grades,
            "formset": formset,
            "segment": loadTemplate,
            "nav_color": "bg-gradient-default",
        }
        return render(self.request, "dashboard/teachers/grades.html", context)

    def post(self, *args, **kwargs):
        operation_form = OperationType(self.request.POST)
        error_message = partial(messages.error, request=self.request)
        success_message = partial(messages.success, request=self.request)
        if operation_form.is_valid():
            operation_type = operation_form.cleaned_data.get("operation")
            match operation_type:
                case "sg":
                    pk = kwargs["pk"]
                    exam = Exam.objects.get(pk=pk)
                    GradeFormset = modelformset_factory(
                        Grade,
                        form=SetGradeForm,
                        max_num=exam.exam_class.student_class.count())
                    formset = GradeFormset(self.request.POST)
                    if formset.is_valid():
                        formset.save()
                        success_message(message=_("Grades submitted successfully."))
                    else:
                        error_message(
                            message=_("Grades cannot exceed the full score."))
                    return redirect("teachers:exams-detail", pk)
                case "de":
                    pk = kwargs["pk"]
                    exam = Exam.objects.get(pk=pk)
                    exam.delete()
                    success_message(message=_("Exam deleted successfully."))
                    return redirect("teachers:exams")
        else:
            error_message(message=_("Provided inputs are invalid."))
            return redirect("teachers:exams")


exam_detail_view = ExamDetailView.as_view()


class StudentsView(PermissionAndLoginRequiredMixin, View):
    permission_required = "teachers.teacher"

    def get(self, *args, **kwargs):
        loadTemplate = self.request.path.split('/')
        students = Student.objects.filter(
            student_class__subjects__teacher__user=self.request.user
        ).distinct()
        return render(self.request, "dashboard/teachers/students.html", {
            "students": students,
            "segment": loadTemplate,
            "nav_color": "bg-gradient-info"
        })


students_view = StudentsView.as_view()


class StudentsDetailView(PermissionAndLoginRequiredMixin, DetailView):
    permission_required = "teachers.teacher"
    template_name = "dashboard/teachers/students_detail.html"
    model = Student

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "nav_color": "bg-gradient-info",
            "segment": self.request.path.split("/")
        })
        return context


students_detail_view = StudentsDetailView.as_view()
