from allauth.account.views import LogoutView
from django.views.generic import View
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import get_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext as _

import random
import string
import logging
import requests

from .forms import PhoneVerificationForm, AddPhonenumberForm
from .models import PhoneNumber

logger = logging.getLogger(__name__)


class CustomLogoutView(LogoutView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["segment"] = "logout"
        return context


logout_view = CustomLogoutView.as_view()


class AddPhoneNumberView(LoginRequiredMixin, View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_name = "account/add_phonenumber.html"
        self.context = dict()

    def get(self, *args, **kwargs):
        add_phonenumber_form = AddPhonenumberForm()
        self.context.update({"form": add_phonenumber_form})
        return render(self.request, self.template_name, self.context)

    def post(self, *args, **kwargs):
        add_phonenumber_form = AddPhonenumberForm(self.request.POST)
        user = get_user(self.request)
        logger.info(f"{user.first_name} requested an OTP.")
        phonenumber_query = PhoneNumber.objects.filter(user=user)

        if phonenumber_query.exists() and not phonenumber_query[0].verified:
            return redirect("verify_phonenumber")
        else:
            if add_phonenumber_form.is_valid():
                users_phonenumber = str(
                    add_phonenumber_form.cleaned_data.get("phone_number"))
                logger.info(
                    f"User {user.username}'s entered phone number is {users_phonenumber}."
                )
                otp_url = "https://portal.amootsms.com/webservice2.asmx/SendWithPattern_REST"
                otp = ''.join(random.choices(string.digits, k=5))
                otp_data = {
                    "UserName": settings.OTPSMS_USERNAME,
                    "Password": settings.OTPSMS_PASSWORD,
                    "Mobile": users_phonenumber,
                    "PatternCodeID": 739,
                    "PatternValues": [user.name(), otp]
                }
                otp_response = requests.post(otp_url, otp_data)
                if otp_response.status_code == 200:
                    logger.info(
                        f"[dark_green]{otp}[/] sent for {self.request.user} - {users_phonenumber}",
                        extra={"markup": True})
                    PhoneNumber.objects.create(user=user,
                                               verification_code=otp,
                                               phonenumber=users_phonenumber)
                    messages.info(self.request,
                                  _("We sent you a verification code."))
                    return redirect("verify_phonenumber")
                else:
                    logger.error(
                        f"[indian_red]Status code {otp_response.status_code}[/]"
                        f" while {user.username} - {users_phonenumber} "
                        "was trying to send a support message.",
                        extra={"markup": True})
                    messages.error(
                        self.request,
                        "Oops... . Something went wrong. Please call us.")
                    return redirect("home:support-page")
            else:
                logger.error(
                    f"Errors happened at add_phonenumber_form:\n{add_phonenumber_form.errors}"
                )
                messages.error(self.request, _("Provided inpurs are invalid."))
                self.context["form"] = add_phonenumber_form
                return render(self.request, self.template_name, self.context)


add_phonenumber_view = AddPhoneNumberView.as_view()


class PhonenumberVerificationView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_name = "account/verify_phonenumber.html"
        self.context = dict()

    def get(self, *args, **kwargs):
        phone_verification_form = PhoneVerificationForm()
        self.context.update({"form": phone_verification_form})
        return render(self.request, self.template_name, self.context)

    def post(self, *args, **kwargs):
        phone_verification_form = PhoneVerificationForm(self.request.POST)
        user = get_user(self.request)
        phonenumber_query = PhoneNumber.objects.filter(user=user)
        if phonenumber_query.exists():
            phonenumber_instance = phonenumber_query[0]
            if phone_verification_form.is_valid():
                entered_code = phone_verification_form.cleaned_data.get(
                    "verification_code")
                logger.info(
                    f"The verificartion code saved for {user.name()} is "
                    f"{phonenumber_instance.verification_code}. "
                    f"The entered code is {entered_code}")
                if entered_code == phonenumber_instance.verification_code:
                    phonenumber_instance.verified = True
                    phonenumber_instance.save()
                    messages.success(self.request,
                                     _("Phone number verified successfully."))
                    logger.info(
                        f"{user.name()} verified their phone number "
                        f"{phonenumber_instance.phonenumber} successfully.")
                    return redirect("home:home")
                else:
                    messages.error(self.request,
                                   _("Entered verification code is wrong."))
                    logger.info(
                        f"{user.name()} entered a wrong verification code.")
                    self.context.update({"form": phone_verification_form})
                    return render(self.request, self.template_name,
                                  self.context)
            else:
                self.context.update({"form": phone_verification_form})
                logger.warning(
                    f"Invalid inputs provided by {user.username}:"
                    f"\n[red]{phone_verification_form.errors}\n{phone_verification_form.non_field_errors()}[/]",
                    extra={"markup": True})
                messages.error(self.request, _("Provided inputs are invalid."))
                return render(self.request, self.template_name, self.context)
        else:
            messages.error(self.request,
                           _("You haven't asked for a verification code yet."))
            return redirect("phonenumber")


phonenumber_verification_view = PhonenumberVerificationView.as_view()
