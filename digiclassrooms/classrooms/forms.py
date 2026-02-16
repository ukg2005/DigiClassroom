from django import forms
from .models import Classroom

class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Physics 101'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Brief description of your classroom'})
        }
