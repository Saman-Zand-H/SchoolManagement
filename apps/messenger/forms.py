from django import forms
from django.contrib.auth import get_user_model

from .models import ChatGroup


class GroupForm(forms.ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['name', 'photo', 'bio']
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "group name e.g. Math101",
                "id": "group-name-field",
            }),
            "photo": forms.FileInput(attrs={
                "class": "form-control",
                "id": "group-photo-field",
            }),
            "bio": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "group bio e.g. Math is fun",
            }),
        }


class MembersForm(forms.Form):
    choices = (
        ("add", "add member"),
        ("delete", "delete member"),
        ("leave", "leave the group"),
    )
    member = forms.CharField(required=False)
    request_type = forms.ChoiceField(choices=choices)
    
    
class ConversationForm(forms.Form):
    conversation_choices = (
        ("group", "create a group"),
        ("pm", "create a private conversation"),
    )
    conversation_type = forms.ChoiceField(choices=conversation_choices, required=False)
    target_user = forms.CharField(required=False)
