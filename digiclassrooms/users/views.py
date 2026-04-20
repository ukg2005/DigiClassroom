from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.timesince import timesince
from django.core.paginator import Paginator
from .forms import UserRegistrationForm
from .models import Notification

@never_cache
@ensure_csrf_cookie
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

@never_cache
@ensure_csrf_cookie
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


@login_required(login_url='login')
def notifications_feed(request):
    recent = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:8]
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    items = [
        {
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'link': n.link,
            'is_read': n.is_read,
            'created': f"{timesince(n.created_at)} ago",
        }
        for n in recent
    ]
    return JsonResponse({'unread_count': unread_count, 'items': items})


@require_POST
@login_required(login_url='login')
def notifications_mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'ok': True})


@require_POST
@login_required(login_url='login')
def notifications_mark_read(request, pk):
    updated = Notification.objects.filter(pk=pk, recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'ok': True, 'updated': bool(updated)})


@login_required(login_url='login')
def notifications_page(request):
    mode = request.GET.get('mode', 'all')
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    if mode == 'unread':
        notifications = notifications.filter(is_read=False)

    paginator = Paginator(notifications, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'users/notifications.html', {
        'page_obj': page_obj,
        'mode': mode,
        'unread_count': Notification.objects.filter(recipient=request.user, is_read=False).count(),
    })