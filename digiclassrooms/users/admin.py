from django.contrib import admin
from .models import Profile, Notification



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'is_teacher', 'is_admin')
	list_filter = ('is_teacher', 'is_admin')
	search_fields = ('user__username', 'user__email')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ('recipient', 'title', 'is_read', 'created_at')
	list_filter = ('is_read', 'created_at')
	search_fields = ('recipient__username', 'title', 'message')