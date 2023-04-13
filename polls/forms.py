from django import forms

class QuestionForm(forms.Form):
    text = forms.CharField(label='', max_length=150)