from django.views import View
from django.db.models import Q
from django.shortcuts import render
from apps.mainapp.mixins import PermissionAndLoginRequiredMixin

from mainapp.models import Assignment, Grade
from mainapp.mixins import PermissionAndLoginRequiredMixin
from teachers.utils import get_charts_labels_ready


class DashboardView(View, PermissionAndLoginRequiredMixin):
    permission_required = "mainapp.student"
    template_name = "dashboard/students/index.html"
    context = dict()

    def get(self, *args, **kwargs):
        student_instance = self.request.user.student_user
        self.context.update({
            "student": student_instance,
            "segment": "home",
            "chart_labels": get_charts_labels_ready()[0],
            "assignments": Assignment.objects.filter(
                assignment_class=student_instance.student_class
            ).order_by("-deadline")[:5],
        })
        return render(self.request, self.template_name, self.context)


dashboard_view = DashboardView.as_view()


class ExamsView(View):
    permission_required = "mainapp.student"
    template_name = "dashboard/students/exams.html"
    context = dict()

    def get(self, *args, **kwargs):
        student_instance = self.request.user.student_user
        grades = Grade.objects.filter(
            Q(exam__exam_class=student_instance.student_class)
            & Q(exam__visible_to_students=True)).order_by("-exam__timestamp")
        self.context.update({
            "grades": grades,
            "segment": self.request.path.split("/"),
            "nav_color": "bg-gradient-indigo"
        })
        return render(self.request, self.template_name, self.context)


exams_view = ExamsView.as_view()
