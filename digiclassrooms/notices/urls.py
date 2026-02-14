from django.urls import path
from . import views

urlpatterns = [
    path('classroom/<int:classroom_pk>/', views.notice_list, name='notices_list'),
    path('classroom/<int:classroom_pk>/create/', views.notice_create, name='notice_create'),
    path('<int:pk>/', views.notice_detail, name='notice_detail'),
]
