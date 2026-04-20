from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('live-counts/', views.dashboard_live_counts, name='dashboard_live_counts'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('setup/', views.setup_classroom, name='setup_classroom'),
    path('enroll/', views.enroll_classroom, name='enroll_classroom'),
    path('join/', views.join_classroom, name='join_classroom'),
    path('join/<int:pk>/', views.join_classroom, name='join_classroom_for_classroom'),
    path('search/', views.search_classrooms, name='search_classrooms'),
    path('classroom/<int:pk>/', views.classroom_detail, name='classroom_detail'),
    path('classroom/<int:pk>/students/<int:student_id>/analytics/', views.student_analytics, name='student_analytics'),
    path('classroom/<int:pk>/leave/', views.leave_classroom, name='leave_classroom'),
    path('classroom/<int:pk>/regenerate-key/', views.regenerate_join_key, name='regenerate_join_key'),
    path('classroom/<int:pk>/request-teacher-join/', views.request_teacher_join_classroom, name='request_teacher_join_classroom'),
    path('teacher-join-request/<int:pk>/cancel/', views.cancel_teacher_join_request, name='cancel_teacher_join_request'),
    path('classroom/<int:pk>/join-settings/', views.update_join_settings, name='update_join_settings'),
    path('classroom/<int:pk>/students/<int:student_id>/remove/', views.remove_student, name='remove_student'),
    path('leave-request/<int:pk>/', views.review_leave_request, name='review_leave_request'),
    path('teacher-join-request/<int:pk>/', views.review_teacher_join_request, name='review_teacher_join_request'),
]
