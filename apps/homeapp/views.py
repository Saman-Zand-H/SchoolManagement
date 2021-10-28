from django.views.generic import TemplateView
from typing import Any, Dict

from mainapp.models import School


class HomePageView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_anonymous:
            context["school"] = School.objects.filter(
                support=self.request.user)
        return context
homepageview = HomePageView.as_view()