from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import UserRegistrationForm

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
        # Add Bootstrap classes to login form fields
        form.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your username'})
        form.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your password'})
    return render(request, 'users/login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('login')