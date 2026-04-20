from django.urls import path
from . import views

urlpatterns = [
    path('global/', views.global_discussion, name='global_discussion'),
    path('global/<int:pk>/delete/', views.delete_global_post, name='delete_global_post'),
    path('classroom/<int:classroom_pk>/discussion/', views.class_discussion, name='class_discussion'),
    path('discussion/<int:pk>/', views.class_discussion_thread, name='class_discussion_thread'),
    path('discussion/<int:pk>/edit/', views.edit_class_discussion_post, name='edit_class_discussion_post'),
    path('discussion/<int:pk>/delete/', views.delete_class_discussion_post, name='delete_class_discussion_post'),
    path('classroom/<int:classroom_pk>/', views.notice_list, name='notices_list'),
    path('classroom/<int:classroom_pk>/create/', views.notice_create, name='notice_create'),
    path('<int:pk>/', views.notice_detail, name='notice_detail'),
    path('<int:pk>/edit/', views.edit_notice, name='edit_notice'),
    path('<int:pk>/delete/', views.delete_notice, name='delete_notice'),
    path('<int:pk>/toggle-pin/', views.toggle_notice_pin, name='toggle_notice_pin'),
    path('<int:pk>/toggle-lock/', views.toggle_notice_thread_lock, name='toggle_notice_thread_lock'),
    path('comment/<int:comment_id>/edit/', views.edit_notice_comment, name='edit_notice_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_notice_comment, name='delete_notice_comment'),
]
