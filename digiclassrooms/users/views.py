from django.shortcuts import render, redirect, get_object_or_404
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
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, SupportTicketForm, SupportReplyForm, UserProfileForm, SupportMessageForm
from .models import Notification, SupportTicket, SupportTicketMessage


def _admin_users_queryset():
    return User.objects.filter(Q(is_superuser=True) | Q(profile__is_admin=True)).distinct()

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


@login_required(login_url='login')
def profile_page(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    tickets = SupportTicket.objects.filter(requester=request.user).order_by('-created_at')
    return render(request, 'users/profile.html', {
        'form': form,
        'tickets': tickets,
        'open_tickets_count': tickets.filter(status=SupportTicket.STATUS_OPEN).count(),
        'in_progress_tickets_count': tickets.filter(status=SupportTicket.STATUS_IN_PROGRESS).count(),
        'resolved_tickets_count': tickets.filter(status=SupportTicket.STATUS_RESOLVED).count(),
        'enrolled_classrooms': request.user.enrolled_classrooms.select_related('teacher').all(),
        'teaching_classrooms': request.user.teaching_classrooms.select_related('teacher').all(),
    })


@login_required(login_url='login')
def support_create(request):
    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.requester = request.user
            ticket.save()
            SupportTicketMessage.objects.create(
                ticket=ticket,
                author=request.user,
                content=ticket.message,
            )

            for admin_user in _admin_users_queryset():
                Notification.objects.create(
                    recipient=admin_user,
                    title=f'New support ticket: {ticket.subject}',
                    message=f'{request.user.username} submitted a {ticket.get_category_display().lower()} ticket.',
                    link='/users/support/inbox/',
                )

            messages.success(request, 'Your message has been sent to the admin team.')
            return redirect('profile')
    else:
        form = SupportTicketForm()

    return render(request, 'users/support_form.html', {'form': form})


@login_required(login_url='login')
def support_inbox(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin)):
        return redirect('profile')

    status_filter = request.GET.get('status', 'open')
    tickets = SupportTicket.objects.select_related('requester').order_by('-created_at')
    if status_filter in {SupportTicket.STATUS_OPEN, SupportTicket.STATUS_IN_PROGRESS, SupportTicket.STATUS_RESOLVED, SupportTicket.STATUS_CLOSED}:
        tickets = tickets.filter(status=status_filter)

    return render(request, 'users/support_inbox.html', {
        'tickets': tickets,
        'status_filter': status_filter,
        'open_count': SupportTicket.objects.filter(status=SupportTicket.STATUS_OPEN).count(),
        'in_progress_count': SupportTicket.objects.filter(status=SupportTicket.STATUS_IN_PROGRESS).count(),
        'resolved_count': SupportTicket.objects.filter(status=SupportTicket.STATUS_RESOLVED).count(),
        'closed_count': SupportTicket.objects.filter(status=SupportTicket.STATUS_CLOSED).count(),
    })


@login_required(login_url='login')
def support_detail(request, pk):
    ticket = get_object_or_404(SupportTicket.objects.select_related('requester'), pk=pk)
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin)
    can_view = is_admin or ticket.requester == request.user
    if not can_view:
        return redirect('profile')

    if request.method == 'POST':
        if ticket.status == SupportTicket.STATUS_CLOSED and not is_admin:
            messages.error(request, 'This ticket is closed.')
            return redirect('support_detail', pk=ticket.pk)

        if is_admin:
            reply_form = SupportReplyForm(request.POST, instance=ticket)
            message_form = SupportMessageForm(request.POST)
        else:
            reply_form = None
            message_form = SupportMessageForm(request.POST)

        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.ticket = ticket
            message.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                message.parent_id = parent_id
            message.save()

            if is_admin:
                ticket.status = request.POST.get('status') or ticket.status
                ticket.admin_reply = message.content
                ticket.replied_at = timezone.now()
                ticket.save(update_fields=['status', 'admin_reply', 'replied_at', 'updated_at'])
                Notification.objects.create(
                    recipient=ticket.requester,
                    title=f'Support update: {ticket.subject}',
                    message='An admin replied to your support ticket.',
                    link=f'/users/support/{ticket.pk}/',
                )
            else:
                if ticket.status == SupportTicket.STATUS_RESOLVED:
                    ticket.status = SupportTicket.STATUS_IN_PROGRESS
                    ticket.save(update_fields=['status', 'updated_at'])
                for admin_user in _admin_users_queryset():
                    Notification.objects.create(
                        recipient=admin_user,
                        title=f'New support reply: {ticket.subject}',
                        message=f'{request.user.username} replied to support ticket #{ticket.pk}.',
                        link=f'/users/support/{ticket.pk}/',
                    )

            messages.success(request, 'Message posted.')
            return redirect('support_detail', pk=ticket.pk)
    else:
        reply_form = SupportReplyForm(instance=ticket) if is_admin else None
        message_form = SupportMessageForm()

    thread_messages = ticket.messages.select_related('author').prefetch_related('replies__author').filter(parent__isnull=True)

    return render(request, 'users/support_detail.html', {
        'ticket': ticket,
        'reply_form': reply_form,
        'message_form': message_form,
        'thread_messages': thread_messages,
        'allow_reply': is_admin or ticket.status != SupportTicket.STATUS_CLOSED,
        'is_admin': is_admin,
    })