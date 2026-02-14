from django import forms
from .models import Lecture, LectureComment

class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['title', 'youtube_link']
        widgets = {
            'youtube_link': forms.URLInput(attrs={
                'placeholder': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={'class': 'form-control'})
        }
        help_texts = {
            'youtube_link': 'Paste any YouTube video URL. Supported formats: youtube.com/watch?v=..., youtu.be/..., youtube.com/embed/...'
        }
    
    def clean_youtube_link(self):
        url = self.cleaned_data.get('youtube_link')
        if url:
            if not ('youtube.com' in url or 'youtu.be' in url):
                raise forms.ValidationError('Please enter a valid YouTube URL')
        return url

class LectureCommentForm(forms.ModelForm):
    class Meta:
        model = LectureComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ask a doubt or comment...'})
        }
