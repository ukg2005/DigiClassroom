from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('setup/', views.setup_classroom, name='setup_classroom'),
    path('enroll/', views.enroll_classroom, name='enroll_classroom'),
    path('classroom/<int:pk>/', views.classroom_detail, name='classroom_detail'),
]
