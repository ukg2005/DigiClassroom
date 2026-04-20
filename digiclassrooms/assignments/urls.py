from django.urls import path
from . import views

urlpatterns = [
    path('classroom/<int:classroom_pk>/', views.assignment_list, name='assignment_list'),
    path('classroom/<int:classroom_pk>/create/', views.assignment_create, name='assignment_create'),
    path('classroom/<int:classroom_pk>/dashboard/', views.teacher_dashboard, name='classroom_analytics'),
    path('classroom/<int:classroom_pk>/calendar/', views.classroom_calendar, name='classroom_calendar'),
    path('classroom/<int:classroom_pk>/calendar/add/', views.add_deadline_event, name='add_deadline_event'),
    path('<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('<int:pk>/edit/', views.edit_assignment, name='edit_assignment'),
    path('<int:pk>/delete/', views.delete_assignment, name='delete_assignment'),
    path('<int:pk>/add_question/', views.add_question, name='add_question'),
    path('<int:pk>/take/', views.take_assignment, name='take_assignment'),
    path('<int:pk>/submissions/', views.view_submissions, name='view_submissions'),
    path('<int:pk>/submissions/export/', views.export_submissions_csv, name='export_submissions'),
    path('submission/<int:pk>/', views.submission_detail, name='submission_detail'),
    path('results/', views.student_results, name='student_results'),
]
