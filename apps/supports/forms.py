from django import forms
from django.utils.translation import gettext_lazy as _

from mainapp.models import Class, Subject, Student
from supports.models import School
from teachers.models import Teacher


class EditOperationType(forms.Form):
    choices = (
        ("uc", "Update class"),
        ("dc", "Delete class"),
        ("ut", "Update teacher"),
        ("dt", "Delete teacher"),
        ("dc", "Delete course"),
        ("us", "Update student"),
        ("ds", "Delete student"),
    )
    operation = forms.ChoiceField(choices=choices, required=False)


class CreateSchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ["name", "support"]
        widgets = {
            "name":
            forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("Name of your school")
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["support"] = forms.IntegerField(required=False)


class EditClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ["class_id", "subjects"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.fields["class_id"] = forms.CharField(
            label=_("Class ID"),
            widget=forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("A unique identifier for class"),
                }),
        )
        if self.request is not None:
            self.fields["subjects"] = forms.ModelMultipleChoiceField(
                widget=forms.CheckboxSelectMultiple(),
                required=False,
                label=_("Courses"),
                queryset=Subject.objects.filter(
                    teacher__school__support=self.request.user),
                to_field_name="pk")
        else:
            self.fields["subjects"] = forms.ModelMultipleChoiceField(
                queryset=Subject.objects.none(),
                widget=forms.CheckboxSelectMultiple())

    def clean_class_id(self):
        class_id = self.cleaned_data.get("class_id")
        class_instance = Class.objects.filter(class_id=class_id)
        if class_instance.exists() and str(self.instance) != str(class_id):
            raise forms.ValidationError(_("This class already exists"),
                                        code="non-unique_class_id")
        return class_id


class CreateClassForm(EditClassForm):
    class Meta:
        model = Class
        fields = ["class_id", "school", "subjects"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["school"].required = False
        self.fields["subjects"].label = _("Courses")


class ChangeTeacherDetails(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ["degree", "university"]
        widgets = {
            "degree": forms.TextInput(attrs={"class": "form-control"}),
            "university": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["university"].required = False
        self.fields["degree"].required = False


class SelectClassesForm(forms.Form):
    classes = forms.ModelMultipleChoiceField(
        Class.objects.all(),
        to_field_name="id",
        widget=forms.CheckboxSelectMultiple(),
        label=_("Classes"))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        if self.request is not None:
            self.fields["classes"].queryset = Class.objects.filter(
                school__support=self.request.user)


class CreateSubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ("name", "teacher")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        if self.request is not None:
            self.fields["teacher"] = forms.ModelChoiceField(
                Teacher.objects.filter(school__support=self.request.user),
                widget=forms.Select(attrs={"class": "form-control"}))
        else:
            self.fields["teacher"] = forms.ModelChoiceField(
                Teacher.objects.none())


class StudentsClassForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["student_class"]

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.request = kwargs.pop("request", None)
        self.fields["student_class"].label = _("Class")
        super().__init__(*args, **kwargs)
        if self.request is not None:
            self.fields["student_class"].queryset = Class.objects.filter(
                school__support=self.request.user)
        else:
            self.fields["student_class"].queryset = Class.objects.none()
