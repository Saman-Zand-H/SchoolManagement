from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.forms import LoginForm, SignupForm
from phonenumber_field.formfields import PhoneNumberField
from django import forms
import logging

from .models import USER_TYPE_CHOICES
from mainapp.models import Class

logger = logging.getLogger(__name__)


def validate_file_extension(file):
    import os

    ext = os.path.splitext(file.name)[1]
    valid_extensions = [".jpg", ".png"]
    if not ext.lower() in valid_extensions:
        raise forms.ValidationError("Unsupported file extension.",
                                    code="invalid_extension")


def validate_file_size(file):
    if file.size > 3 * 1024 ** 2:
        raise forms.ValidationError("Maximum file size is 3MB.",
                                    code="invalid_filesize")


class BaseSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=254,
        min_length=2,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "enter your first name"}))
    last_name = forms.CharField(
        max_length=254,
        min_length=2,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "enter your last name",}))
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=False)
    picture = forms.ImageField(
        required=False,
        label="Avatar Picture",
        validators=[validate_file_extension, validate_file_size],
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control",
        }))
    phone_number = PhoneNumberField(widget=forms.TextInput(
        attrs={
            "class": "form-control",
            "placeholder": "like 09xxxxxxxx"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"] = forms.CharField(
            max_length=20,
            min_length=2,
            label="ID",
            widget=forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "User ID",
            }),
        )
        self.fields["email"] = forms.EmailField(
            widget=forms.EmailInput(attrs={
                "class": "form-control",
            }),
            required=False,
        )
        self.fields["password1"] = forms.CharField(
            max_length=20,
            min_length=2,
            label="Password",
            widget=forms.PasswordInput(attrs={
                "class": "form-control",
                "placeholder": "Password",
            }),
        )
        self.fields["password2"] = forms.CharField(
            max_length=20,
            min_length=2,
            label="Confirm Password",
            widget=forms.PasswordInput(attrs={
                "class": "form-control",
                "placeholder": "Confirm Password",
            }),
        )

    def clean_password2(self):
        if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
            raise forms.ValidationError("Passwords should not be different.",
                                        code="invalid_confirm_password")
        return self.cleaned_data["password2"]

    def save(self, request):
        user = super().save(request)
        if self.cleaned_data.get("picture"):
            user.picture = self.cleaned_data.get("picture")
        user.user_type = self.cleaned_data.get("user_type")
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.phone_number = self.cleaned_data.get("phone_number")
        user.save()
        return user


class CustomSignUpAdapter(DefaultAccountAdapter):
    def clean_username(self, username, shallow=False):
        try:
            super().clean_username(username, shallow=shallow)
        except forms.ValidationError:
            raise forms.ValidationError("This ID already exists.",
                                        code="nonunique_username")
        return username


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        user = super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields["login"] = forms.CharField(
            max_length=20,
            min_length=2,
            label="ID",
            widget=forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Your ID",
            }),
        )
        self.fields["password"] = forms.CharField(
            max_length=20,
            min_length=2,
            label="Password",
            widget=forms.PasswordInput(attrs={
                "class": "form-control",
                "placeholder": "Password",
            }),
        )
        return user


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