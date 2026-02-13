from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('change_password/', auth_views.PasswordChangeView.as_view(template_name='users/change_password.html'), name='change_password'),
    path('change_password_done/', auth_views.PasswordChangeDoneView.as_view(template_name='users/change_password_done.html'), name='password_change_done'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='users/reset_password.html'), name='reset_password'),
    path('reset_password_done/', auth_views.PasswordResetDoneView.as_view(template_name='users/reset_password_done.html'), name='password_reset_done'),
    path('reset_password_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/reset_password_confirm.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/reset_password_complete.html'), name='password_reset_complete'),
]
