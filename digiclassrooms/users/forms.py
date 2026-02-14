from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_teacher = forms.BooleanField(label='I am a Teacher', required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            if hasattr(user, 'profile'):
                user.profile.is_teacher = self.cleaned_data.get('is_teacher')
                user.profile.save()
        return user
