from django.urls import path
from . import views

urlpatterns = [
    path('classroom/<int:classroom_pk>/', views.lecture_list, name='lectures_list'),
    path('classroom/<int:classroom_pk>/create/', views.lecture_create, name='lecture_create'),
    path('<int:pk>/', views.lecture_detail, name='lecture_detail'),
]
