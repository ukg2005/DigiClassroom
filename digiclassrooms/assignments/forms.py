from django import forms
from .models import Assignment

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title']

class QuestionForm(forms.Form):
    question_text = forms.CharField(max_length=500, label='Question')
    option1 = forms.CharField(max_length=200, label='Option 1')
    option2 = forms.CharField(max_length=200, label='Option 2')
    option3 = forms.CharField(max_length=200, label='Option 3')
    option4 = forms.CharField(max_length=200, label='Option 4')
    correct_option = forms.ChoiceField(choices=[('1', 'Option 1'), ('2', 'Option 2'), ('3', 'Option 3'), ('4', 'Option 4')], widget=forms.RadioSelect)
