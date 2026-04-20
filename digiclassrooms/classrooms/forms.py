from django import forms
from django.contrib.auth.models import User
from .models import Classroom

class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Physics 101'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Brief description of your classroom'})
        }


class AdminClassroomForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__is_teacher=True).order_by('username'),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Classroom
        fields = ['name', 'description', 'teacher']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Physics 101'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Brief description of the classroom'}),
        }


class JoinClassroomForm(forms.Form):
    join_key = forms.CharField(
        max_length=8,
        min_length=8,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter 8-character join key',
                'autocomplete': 'off',
            }
        ),
    )

    def clean_join_key(self):
        return self.cleaned_data['join_key'].strip().upper()


class ClassJoinSettingsForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['joins_enabled', 'join_key_ttl_override_minutes']
        widgets = {
            'joins_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'join_key_ttl_override_minutes': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 1,
                    'placeholder': 'Leave blank to use global default',
                }
            ),
        }

    def clean_join_key_ttl_override_minutes(self):
        ttl = self.cleaned_data.get('join_key_ttl_override_minutes')
        if ttl is not None and ttl < 1:
            raise forms.ValidationError('TTL must be at least 1 minute.')
        return ttl
