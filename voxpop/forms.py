from django import forms

from .models import Question
from .models import Voxpop

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text"]

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