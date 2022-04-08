import django_filters
from django_filters import FilterSet
from django.forms.widgets import TextInput

from mainapp.models import Exam

class ExamFilter(FilterSet):
    subject__name = django_filters.CharFilter(
        label="Subject",
        required=False,
        widget=TextInput(attrs={
        "placeholder": "Subject name... e.g. Math",
    }))
    exam_class__class_id = django_filters.CharFilter(
        lookup_expr='icontains',
        label="Class",
        required=False,
        widget=TextInput(attrs={
            "placeholder": "Class name... e.g. Biology101",
        }),
    )
    timestamp = django_filters.DateTimeFromToRangeFilter(
        field_name='timestamp', 
        required=False,
        label="Time range",
        widget=django_filters.widgets.RangeWidget(
            attrs={
                'placeholder': 'YYYY-MM-DD',
                'class': 'form-control datepicker',
            },
        ),
    )
    
    class Meta:
        model = Exam
        fields = ['subject__name', 'exam_class__class_id', 'timestamp']
        