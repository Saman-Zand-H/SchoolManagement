from django import forms

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
        ("da", "Delete article"),
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
                "placeholder": "Name of your school"
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
            label="Class ID",
            widget=forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "A unique identifier for class",
                }),
        )
        
        if self.request is not None:
            user = getattr(self.request, "user")
            self.fields["subjects"] = forms.ModelMultipleChoiceField(
                widget=forms.CheckboxSelectMultiple(),
                required=False,
                label="Courses",
                queryset=Subject.objects.filter(
                    teacher__school__support=user).distinct(),
                to_field_name="pk",
            )
        else:
            self.fields["subjects"] = forms.ModelMultipleChoiceField(
                queryset=Subject.objects.none(),
                widget=forms.CheckboxSelectMultiple())

    def clean_class_id(self):
        class_id = self.cleaned_data.get("class_id")
        class_instance = Class.objects.filter(class_id=class_id)
        if class_instance.exists() and str(self.instance) != str(class_id):
            raise forms.ValidationError("This class already exists",
                                        code="non-unique_class_id")
        return class_id


class CreateClassForm(EditClassForm):
    class Meta:
        model = Class
        fields = ["class_id", "school", "subjects"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["school"].required = False
        self.fields["subjects"].label = "Courses"


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
        label="Classes",
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        if self.request is not None:
            self.fields["classes"].queryset = Class.objects.filter(
                school__support=self.request.user).distinct()


class CreateSubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ("name", "teacher")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        if self.request is not None:
            self.fields["teacher"] = forms.ModelChoiceField(
                Teacher.objects.filter(school__support=self.request.user).distinct(),
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
        self.fields["student_class"].label = "Class"
        super().__init__(*args, **kwargs)
        if self.request is not None:
            self.fields["student_class"].queryset = Class.objects.filter(
                school__support=self.request.user)
        else:
            self.fields["student_class"].queryset = Class.objects.none()
