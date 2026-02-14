from django.urls import path
from . import views

urlpatterns = [
    path('classroom/<int:classroom_pk>/', views.assignment_list, name='assignment_list'),
    path('classroom/<int:classroom_pk>/create/', views.assignment_create, name='assignment_create'),
    path('<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('<int:pk>/add_question/', views.add_question, name='add_question'),
    path('<int:pk>/take/', views.take_assignment, name='take_assignment'),
    path('<int:pk>/submissions/', views.view_submissions, name='view_submissions'),
    path('submission/<int:pk>/', views.submission_detail, name='submission_detail'),
]
