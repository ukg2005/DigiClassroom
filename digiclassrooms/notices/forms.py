from django import forms
from .models import Notice, NoticeComment

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Notice title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Notice content'})
        }

class NoticeCommentForm(forms.ModelForm):
    class Meta:
        model = NoticeComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write a comment...', 'class': 'form-control'})
        }
        labels = {
            'content': ''
        }
