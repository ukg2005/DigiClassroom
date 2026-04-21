from django.contrib import admin
from .models import Profile, Notification, SupportTicket, SupportTicketMessage



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


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
	list_display = ('requester', 'category', 'subject', 'status', 'created_at', 'replied_at')
	list_filter = ('category', 'status', 'created_at')
	search_fields = ('requester__username', 'subject', 'message', 'admin_reply')


@admin.register(SupportTicketMessage)
class SupportTicketMessageAdmin(admin.ModelAdmin):
	list_display = ('ticket', 'author', 'created_at')
	search_fields = ('ticket__subject', 'author__username', 'content')