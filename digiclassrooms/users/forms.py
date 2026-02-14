from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    is_teacher = forms.BooleanField(label='I am a Teacher', required=False)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'is_teacher']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            is_teacher = self.cleaned_data.get('is_teacher')
            Profile.objects.create(user=user, is_teacher=is_teacher)
        return user