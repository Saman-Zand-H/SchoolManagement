from random import choices
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.forms import (LoginForm, 
                                   SignupForm, 
                                   ResetPasswordForm, 
                                   AddEmailForm)
from django import forms

import logging

from mainapp.models import Class


logger = logging.getLogger(__name__)


def validate_file_extension(file):
    import os
    ext = os.path.splitext(file.name)[1]
    valid_extensions = [".jpg", ".png"]
    if not ext.lower() in valid_extensions:
        logger.info("An invalid file was detected, and rejected.")
        raise forms.ValidationError("Unsupported file extension.",
                                    code="invalid_extension")


def validate_file_size(file):
    if file.size > 3 * 1024**2:
        logger.info("An invalid file was detected, and rejected.")
        raise forms.ValidationError("Maximum file size is 3MB.",
                                    code="invalid_filesize")


class BaseSignupForm(SignupForm):
    USER_TYPE_CHOICES = (
        ("S", "student"),
        ("T", "teacher"),
        ("SS", "support staff"),
    )
    first_name = forms.CharField(
        max_length=254,
        min_length=2,
        label="Firstname",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "enter your first name",
        }))
    last_name = forms.CharField(
        max_length=254,
        min_length=2,
        label="Lastname",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "enter your last name",
        }))
    picture = forms.ImageField(
        required=False,
        label="Avatar Picture",
        validators=[validate_file_extension, validate_file_size],
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control",
        }))
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES,
                                  widget=forms.HiddenInput,
                                  required=False)
    
    def __init__(self,request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.fields["username"].widget = forms.TextInput(attrs={
            "placeholder": "enter your username",
            "class": "form-control",
            "id": "username",
        })
        self.fields["password1"].widget = forms.PasswordInput(attrs={
            "placeholder": "enter your password",
            "class": "form-control",
            "id": "password1",
        })
        self.fields["password2"].widget = forms.PasswordInput(attrs={
            "placeholder": "enter your password again",
            "class": "form-control",
            "id": "password2",
        })
        self.fields["email"] = forms.EmailField(
            widget=forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. example@example.com",
                }),
            
            label="E-Mail Address",
            required=False,
        )
    

class CustomSignUpAdapter(DefaultAccountAdapter):
    
    def save_user(self, request, user, form, commit=True):
        from allauth.account.utils import user_field
        data = form.cleaned_data
        user_field(user, "picture", data.get("picture"))
        user_field(user, "user_type", data.get("user_type"))
        user = super().save_user(request, user, form, commit)
        return user


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["login"] = forms.CharField(
            max_length=20,
            min_length=2,
            label="Your ID",
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


class CustomPasswordResetForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"] = forms.EmailField(
            label="E-Mail Address",
            widget=forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. example@example.com"
                }))


class CustomAddEmailForm(AddEmailForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"] = forms.EmailField(
            widget=forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. example@example.com"
                }),
            label="E-Mail Address")

class SupportStudentSignupForm(BaseSignupForm):
    student_class = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        to_field_name="id",
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        if self.request is not None:
            self.fields["student_class"].queryset = Class.objects.filter(
                school=self.request.user.school)
        else:
            self.fields["student_class"].queryset = Class.objects.none() 
            
    def clean(self):
        if self.cleaned_data.get("user_type") != "S":
            raise forms.ValidationError({"user_type": "Invalid user type."})
        return super().clean()


class SupportTeacherSignupForm(BaseSignupForm):
    
    def clean(self):
        if self.cleaned_data.get("user_type") != "T":
            raise forms.ValidationError({"user_type": "Invalid user type."})
        return super().clean()

class SupportSignupForm(BaseSignupForm):    
    
    def clean(self):
        if self.cleaned_data.get("user_type") != "SS":
            raise forms.ValidationError({"user_type": "Invalid user type."})
        return super().clean()


class UserBioForm(forms.Form):
    about = forms.CharField(required=False)
