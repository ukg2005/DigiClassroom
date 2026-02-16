from django import forms
from .models import Assignment

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Chapter 1 Quiz'})
        }

class QuestionForm(forms.Form):
    question_text = forms.CharField(
        max_length=500, 
        label='Question',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    option1 = forms.CharField(
        max_length=200, 
        label='Option 1',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    option2 = forms.CharField(
        max_length=200, 
        label='Option 2',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    option3 = forms.CharField(
        max_length=200, 
        label='Option 3',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    option4 = forms.CharField(
        max_length=200, 
        label='Option 4',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    correct_option = forms.ChoiceField(
        choices=[('1', 'Option 1'), ('2', 'Option 2'), ('3', 'Option 3'), ('4', 'Option 4')], 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
