from django import forms
from .models import Notice, NoticeComment

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content']

class NoticeCommentForm(forms.ModelForm):
    class Meta:
        model = NoticeComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Write a comment...'})
        }
