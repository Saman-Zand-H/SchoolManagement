from allauth.account.forms import LoginForm, SignupForm

from django import forms

from .models import USER_TYPE_CHOICES


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        user = super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields["login"] = forms.CharField(
            max_length=20, min_length=2, label="ID", widget=forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Your Given ID",
            }))
        self.fields["password"] = forms.CharField(
            max_length=20, min_length=2, label="ID", widget=forms.PasswordInput(attrs={
                "class": "form-control",
                "placeholder": "Password",
            }))
        return user


class CustomSignupForm(SignupForm):
    name = forms.CharField(max_length=254, min_length=2, widget=forms.TextInput(attrs={
        "placeholder": "hello",
    }))
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES)
    picture = forms.ImageField()

    def __init__(self, *args, **kwargs):
        user = super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.fields["username"] = forms.CharField(
            max_length=20, min_length=2, label="ID", widget=forms.TextInput(attrs={
                "class": "form-control",
            }))
        return user

    def save(self, *args, **kwargs):
        user = super(CustomLoginForm, self).login(*args, **kwargs)
        self.picture = self.cleaned_data.get('picture')
        self.user_type = self.cleaned_data.get("user_type")
        self.name = self.cleaned_data.get('name')

        return user
