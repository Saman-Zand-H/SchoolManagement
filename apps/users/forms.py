from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.forms import LoginForm, SignupForm
from phonenumber_field.formfields import PhoneNumberField
from django.utils.translation import gettext as _
from django import forms

import logging

from .models import USER_TYPE_CHOICES
from mainapp.models import Class

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='[%(levelname)s] %(asctime)s - %(name)s: %(message)s')
logger.setLevel(logging.DEBUG)


def validate_file_extension(file):
    import os
    ext = os.path.splitext(file.name)[1]
    valid_extensions = [".jpg", ".png"]
    if not ext.lower() in valid_extensions:
        logger.info("An invalid file was detected, and rejected.")
        raise forms.ValidationError(_("Unsupported file extension."),
                                    code="invalid_extension")


def validate_file_size(file):
    if file.size > 3 * 1024**2:
        logger.info("An invalid file was detected, and rejected.")
        raise forms.ValidationError(_("Maximum file size is 3MB."),
                                    code="invalid_filesize")


class BaseSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=254,
        min_length=2,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": _("enter your first name"),
        }))
    last_name = forms.CharField(
        max_length=254,
        min_length=2,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": _("enter your last name"),
        }))
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=False)
    picture = forms.ImageField(
        required=False,
        label=_("Avatar Picture"),
        validators=[validate_file_extension, validate_file_size],
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control",
        }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"] = forms.CharField(
            max_length=20,
            min_length=2,
            label="ID",
            widget=forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("User ID"),
            }),
        )
        self.fields["email"] = forms.EmailField(
            widget=forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "example@example.XXX",
            }),
            required=False,
        )
        self.fields["password1"] = forms.CharField(
            max_length=20,
            min_length=2,
            label="Password",
            widget=forms.PasswordInput(attrs={
                "class": "form-control",
                "placeholder": _("Password"),
            }),
        )
        self.fields["password2"] = forms.CharField(
            max_length=20,
            min_length=2,
            label=_("Confirm Password"),
            widget=forms.PasswordInput(attrs={
                "class": "form-control",
                "placeholder": _("Confirm Password"),
            }),
        )

    def save(self, request):
        user = super().save(request)
        if self.cleaned_data.get("picture"):
            user.picture = self.cleaned_data.get("picture")
        user.user_type = self.cleaned_data.get("user_type")
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.save()
        return user


class CustomSignUpAdapter(DefaultAccountAdapter):
    def clean_username(self, username, shallow=False):
        try:
            super().clean_username(username, shallow=shallow)
        except forms.ValidationError:
            raise forms.ValidationError(_("This ID already exists."),
                                        code="indistinct_username")
        return username


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        self.error_messages.update({
            "students_not_allowed":
            "Sorry. We don't support students currently.",
        })
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields["login"] = forms.CharField(
            max_length=20,
            min_length=2,
            label="ID",
            widget=forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("Your ID"),
            }),
        )
        self.fields["password"] = forms.CharField(
            max_length=20,
            min_length=2,
            label="Password",
            widget=forms.PasswordInput(attrs={
                "class": "form-control",
                "placeholder": _("Password"),
            }),
        )

    def clean(self):
        super().clean()
        if self.user:
            if self.user.user_type == "S":
                logger.info(
                    f"A student with id {self.user.user_id} was trying to sign in."
                )
                raise forms.ValidationError(
                    self.error_messages["students_not_allowed"],
                    code="students_not_allowed")
        return self.cleaned_data


class AddPhonenumberForm(forms.Form):
    phone_number = PhoneNumberField(widget=forms.TextInput(
        attrs={
            "class": "form-control",
            "placeholder": _("like") + " 09xxxxxxxxx"
        }))


class PhoneVerificationForm(forms.Form):
    users_input = forms.CharField(widget=forms.TextInput(
        attrs={
            "class": "form-control",
            "placeholder": _("please enter the code sent to you")
        }))


class SupportStudentSignupForm(BaseSignupForm):
    student_class = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        to_field_name="id",
    )

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        if request is not None:
            self.fields["student_class"].queryset = Class.objects.filter(
                school__support=request.user)


class UserBioForm(forms.Form):
    about = forms.CharField(required=False)
