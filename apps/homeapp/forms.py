from django.utils.translation import gettext_lazy as _
from django import forms
from ckeditor.widgets import CKEditorWidget

from mainapp.models import Article, Assignment, Subject, Class


class OperationType(forms.Form):
    choices = (
        ("ea", "Edit assignment"),
        
    )
    operation = forms.ChoiceField(choices=choices, required=False)


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


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['author', 'school']
        widgets = {
            "title":
            forms.TextInput(attrs={
                "class": "form-control",
                "id": "article-title",
            }),
            "categories":
            forms.TextInput(attrs={
                "class": "form-control",
                "id": "article-categories",
            }),
            "text":
            CKEditorWidget(attrs={
                "class": "form-control",
                "id": "article-text",
            },
                extra_plugins="mathjax"),
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        exclude = ["timestamp"]
        widgets = {
            "deadline": forms.DateInput(attrs={
                "class": "datepicker",
            })
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = getattr(request, "user")
        self.fields.get("assignment_class").queryset = Class.objects.filter(
            subjects__teacher__user=user)
        self.fields.get("subject").queryset = Subject.objects.filter(
            teacher__user=user)
