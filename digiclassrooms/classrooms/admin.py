from django.contrib import admin
from .models import Classroom, ClassroomLeaveRequest, ClassroomTeacherJoinRequest



@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
	list_display = ('name', 'teacher', 'created_by', 'joins_enabled', 'created_at')
	list_filter = ('joins_enabled', 'created_at')
	search_fields = ('name', 'description', 'teacher__username', 'created_by__username')
	filter_horizontal = ('teachers', 'students')


@admin.register(ClassroomLeaveRequest)
class ClassroomLeaveRequestAdmin(admin.ModelAdmin):
	list_display = ('classroom', 'requester', 'role', 'status', 'requested_at', 'reviewed_by')
	list_filter = ('role', 'status', 'requested_at')
	search_fields = ('classroom__name', 'requester__username')


@admin.register(ClassroomTeacherJoinRequest)
class ClassroomTeacherJoinRequestAdmin(admin.ModelAdmin):
	list_display = ('classroom', 'requester', 'status', 'requested_at', 'reviewed_by')
	list_filter = ('status', 'requested_at')
	search_fields = ('classroom__name', 'requester__username')