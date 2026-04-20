from django.contrib import admin
from .models import Notice, NoticeComment, GlobalDiscussionPost, ClassDiscussionPost



@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
	list_display = ('title', 'classroom', 'author', 'is_pinned', 'is_thread_locked', 'created_at')
	list_filter = ('is_pinned', 'is_thread_locked', 'created_at')
	search_fields = ('title', 'content', 'classroom__name', 'author__username')


@admin.register(NoticeComment)
class NoticeCommentAdmin(admin.ModelAdmin):
	list_display = ('notice', 'author', 'created_at', 'is_edited')
	list_filter = ('is_edited', 'created_at')
	search_fields = ('notice__title', 'author__username', 'content')


@admin.register(GlobalDiscussionPost)
class GlobalDiscussionPostAdmin(admin.ModelAdmin):
	list_display = ('author', 'created_at', 'content')
	search_fields = ('author__username', 'content')


@admin.register(ClassDiscussionPost)
class ClassDiscussionPostAdmin(admin.ModelAdmin):
	list_display = ('classroom', 'author', 'parent', 'created_at', 'is_edited')
	list_filter = ('is_edited', 'created_at')
	search_fields = ('classroom__name', 'author__username', 'content')