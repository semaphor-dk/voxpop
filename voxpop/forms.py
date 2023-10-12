from django import forms

from .models import Question
from .models import Voxpop


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            "text",
            "display_name",
        ]


class VoxpopForm(forms.ModelForm):
    class Meta:
        model = Voxpop
        fields = [
            "title",
            "description",
            "starts_at",
            "expires_at",
            "is_moderated",
            "allow_anonymous",
        ]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "starts_at": forms.DateInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%d %H:%M",
            ),
            "expires_at": forms.DateInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%d %H:%M",
            ),
        }
