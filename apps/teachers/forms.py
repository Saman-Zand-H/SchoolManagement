from django import forms
from django.utils.translation import gettext as _
from ckeditor.widgets import CKEditorWidget

from decimal import Decimal
from mainapp.models import Grade, Article


class ExamForm(forms.Form):
    subject = forms.CharField(required=False)
    exam_class = forms.IntegerField(required=False)
    full_score = forms.DecimalField(required=False)
    timestamp = forms.DateField(required=False)


class FilterExamsForm(forms.Form):
    dateSince = forms.DateField(required=False)
    dateTill = forms.DateField(required=False)
    subjectFilter = forms.IntegerField(required=False)
    classFilter = forms.IntegerField(required=False)


class SetGradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ["grade", "student", "exam"]

        widgets = {
            "grade": forms.NumberInput(attrs={
                "class": "form-control w-50",
            }),
            "student": forms.HiddenInput(),
            "exam": forms.HiddenInput(),
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields["student"].required = False
        self.fields["exam"].required = False

    def clean_grade(self):
        grade = self.cleaned_data.get("grade")
        if not isinstance(grade, Decimal):
            raise forms.ValidationError(_("Provided grade is not valid."))
        return grade


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
