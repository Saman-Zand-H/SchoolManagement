from allauth.account.views import LogoutView
from django.views.generic import View
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import get_user
from django.contrib import messages

import requests

from .forms import PhoneVerificationForm, AddPhonenumberForm


class CustomLogoutView(LogoutView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["segment"] = "logout"
        return context


logout_view = CustomLogoutView.as_view()


class AddPhoneNumberView(View):
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
        if add_phonenumber_form.is_valid():
            users_phonenumber = str(
                add_phonenumber_form.cleaned_data.get("phone_number"))
            otpsms_url = "https://portal.amootsms.com/webservice2.asmx/SendQuickOTP_REST"
            otpsms_data = {
                "UserName": settings.OTPSMS_USERNAME,
                "Password": settings.OTPSMS_PASSWORD,
                "Mobile": users_phonenumber,
                "CodeLength": 5,
                "LineNumber": settings.OTPSMS_LINENUMBER,
            }
            otpsms_response = requests.post(otpsms_url, otpsms_data)
            if otpsms_response.status_code == 200 and otpsms_response.json(
            )["Status"] == "Success":
                otp_code = otpsms_response.json()["Code"]
                user = get_user(self.request)
                user.phonenumber_verification_code = otp_code
                user.save()
                messages.info(self.request, "We sent you a verification code.")
                return redirect("verify_phonenumber")
            else:
                print(otpsms_response.status_code)
                messages.error(
                    self.request,
                    "Oops... . Something went wrong. Please call us.")
                return redirect("home:support-page")
        else:
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


phonenumber_verification_view = PhonenumberVerificationView.as_view()
