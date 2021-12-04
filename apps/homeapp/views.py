from django.views.generic import TemplateView, View
from django.utils.translation import gettext as _
from django.utils.translation import activate
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.conf import settings

import logging
from typing import Any, Dict
import requests

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
        if form.is_valid():
            users_name = form.cleaned_data.get("name")
            users_email = form.cleaned_data.get("email")
            users_text = form.cleaned_data.get("text")
            email_url = "https://email-sender1.p.rapidapi.com/"
            querystring = {
                "txt_msg": users_text,
                "to": "clientdjs@gmail.com",
                "from": "DJS School-Management-System",
                "subject": "Support",
                "bcc": "bcc-mail@gmail.com",
                "reply_to": "samanzandh@gmail.com@gmail.com",
                "html_msg": f"""
                            <html><body>
                                <h1>{_("DJSchool Support")}</h1>
                                <h3>{users_name}- {users_email}</h3>
                                <pre>{users_text}</pre>
                            </body></html>""",
                "cc": "cc-mail@gmail.com"
            }
            payload = "{\"key1\": \"value\", \"key2\": \"value\"}"
            headers = {
                'content-type': "application/json",
                'x-rapidapi-host': settings.EMAIL_API_HOST,
                'x-rapidapi-key': settings.EMAIL_API_KEY
            }
            response = requests.request("POST",
                                        email_url,
                                        data=payload,
                                        headers=headers,
                                        params=querystring)
            if response.status_code == 200:
                messages.success(
                    self.request,
                    _("Thanks for your message. Message sent successfully."))
            else:
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
    print(request.method)
    if request.method == "POST":
        user_language = request.POST.get("language")
        logger.warning(user_language)
        activate(user_language)
        response = HttpResponseRedirect(reverse("home:home"))
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
        return response
    return redirect("home:home")
