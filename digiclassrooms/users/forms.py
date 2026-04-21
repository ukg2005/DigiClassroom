from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from .models import Profile, SupportTicket, SupportTicketMessage

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'})
    )
    user_type = forms.ChoiceField(
        choices=[('student', 'Student'), ('teacher', 'Teacher')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='I am a'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter a secure password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm your password'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            if hasattr(user, 'profile'):
                user.profile.is_teacher = (self.cleaned_data.get('user_type') == 'teacher')
                user.profile.save()
        return user


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your email address'})


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter new password'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm new password'})


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter current password'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter new password'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm new password'})


class UserProfileForm(forms.ModelForm):
    roll_no = forms.CharField(
        required=False,
        max_length=32,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter roll number'})
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile = getattr(self.instance, 'profile', None)
        if profile:
            self.fields['roll_no'].initial = profile.roll_no

    def save(self, commit=True):
        user = super().save(commit=commit)
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.roll_no = self.cleaned_data.get('roll_no', '').strip()
        profile.save(update_fields=['roll_no'])
        return user


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['category', 'subject', 'message']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief summary of what you need help with'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe the issue, complaint, or question'}),
        }


class SupportReplyForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['status', 'admin_reply']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_reply': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your reply to the user'}),
        }


class SupportMessageForm(forms.ModelForm):
    class Meta:
        model = SupportTicketMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your reply'}),
        }
