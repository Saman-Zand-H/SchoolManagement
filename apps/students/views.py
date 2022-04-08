from django.views import View
from django.shortcuts import render, get_object_or_404

from mainapp.models import Student, Assignment
from teachers.views import get_charts_labels_ready


class DashboardView(View):
    template_name = "dashboard/students/index.html"
    context = dict()
    
    def get(self, *args, **kwargs):
        student_instance = get_object_or_404(Student, user=self.request.user)
        self.context.update({
            "student": student_instance,
            "chart_labels": get_charts_labels_ready()[0],
            "assignments": Assignment.objects.filter(
                assignment_class=student_instance.student_class).order_by("-deadline")[:5],
        })
        return render(self.request, self.template_name, self.context)
    

dashboard_view = DashboardView.as_view()
