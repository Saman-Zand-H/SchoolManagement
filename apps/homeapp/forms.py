from django.utils.translation import ugettext_lazy as _
from django import forms


class SupportForm(forms.Form):
    name = forms.CharField(
        label=_("Name"),
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": _("e.g. John Gobbles"),
        }))
    email = forms.EmailField(
        label=_("Email Address"),
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": _("e.g. example@example.com"),
            }))
    text = forms.CharField(
        label=_("Issues or Requests"),
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": _("here goes your text...."),
        }))
