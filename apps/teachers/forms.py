from django import forms

from mainapp.models import *


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
        init = super().__init__(**kwargs)
        self.fields["student"].required = False
        self.fields["exam"].required = False
        return init


class SetUserBiographyForm(forms.Form):
    about = forms.CharField(required=False)
