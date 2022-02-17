from django.views.generic import TemplateView, View
from django.utils.translation import gettext as _
from django.utils.translation import activate
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.core.mail import mail_admins

import logging
from typing import Any, Dict
from smtplib import SMTPException

from mainapp.models import School
from .forms import SupportForm

logger = logging.getLogger(__name__)


class HomePageView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_anonymous:
            context["school"] = School.objects.filter(
                support=self.request.user)
        return context


homepageview = HomePageView.as_view()


class SupportView(View):
    def get(self, *args, **kwargs):
        return render(self.request, "dashboard/support.html", {
            "form": SupportForm(),
            "segment": "support-page"
        })

    def post(self, *args, **kwargs):
        form = SupportForm(self.request.POST)
        logger.info(
            f"[blue]{self.request.user} tried to send a support message.[/]",
            extra={"markup": True})

        if form.is_valid():
            users_name = form.cleaned_data.get("name")
            users_email = form.cleaned_data.get("email")
            users_text = form.cleaned_data.get("text")
            try:
                mail_admins(f"DjS-School Supprt by {users_name}",
                            users_text,
                            html_message=f"""
                    <html>
                        <body>
                            <h1>{_("DjSchool Support")}</h1>
                            <h3>{users_name}- {users_email}</h3>
                            <pre>{users_text}</pre>
                        </body>
                    </html>""")
                logger.info(
                    f"[green]User {self.request.user} succesfully sent a support message.[/]",
                    extra={"markup": True})
                messages.success(
                    self.request,
                    _("Thanks for your message. Message sent successfully."))
            except SMTPException as e:
                logger.error(
                    f"[red]There was an error while user {self.request.user} "
                    "was trying to send a support message! The problem "
                    "caused by the email API.[/]",
                    extra={"markup": True})
                logger.error(f"The error: {e}")
                messages.error(
                    self.request,
                    _("An internal error happened. Please call us as soon as you can."
                      ))
            return redirect("home:support-page")
        else:
            messages.error(self.request, _("Provided inputs are invalid."))
            return render(self.request, "dashboard/support.html",
                          {"form": form})


support_view = SupportView.as_view()


def set_language(request):
    if request.method == "POST":
        user_language = request.POST.get("language")
        activate(user_language)
        response = HttpResponseRedirect(reverse("home:home"))
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
        return response

    return redirect("home:home")
