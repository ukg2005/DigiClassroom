from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm, CustomPasswordChangeForm

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('profile/', views.profile_page, name='profile'),
    path('support/', views.support_create, name='support_create'),
    path('support/inbox/', views.support_inbox, name='support_inbox'),
    path('support/<int:pk>/', views.support_detail, name='support_detail'),
    path('change_password/', auth_views.PasswordChangeView.as_view(
        template_name='users/change_password.html',
        form_class=CustomPasswordChangeForm
    ), name='change_password'),
    path('change_password_done/', auth_views.PasswordChangeDoneView.as_view(template_name='users/change_password_done.html'), name='password_change_done'),
    path('reset_password/', auth_views.PasswordResetView.as_view(
        template_name='users/reset_password.html',
        form_class=CustomPasswordResetForm
    ), name='reset_password'),
    path('reset_password_done/', auth_views.PasswordResetDoneView.as_view(template_name='users/reset_password_done.html'), name='password_reset_done'),
    path('reset_password_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/reset_password_confirm.html',
        form_class=CustomSetPasswordForm
    ), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/reset_password_complete.html'), name='password_reset_complete'),
    path('notifications/', views.notifications_page, name='notifications_page'),
    path('notifications/feed/', views.notifications_feed, name='notifications_feed'),
    path('notifications/mark-all-read/', views.notifications_mark_all_read, name='notifications_mark_all_read'),
    path('notifications/<int:pk>/mark-read/', views.notifications_mark_read, name='notifications_mark_read'),
]
