from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add', views.add, name='add_video'),
    path('video_list', views.video_list, name='video_list'),
    path('video_detail/<int:video_pk>', views.video_detail, name='video_detail'),
    path('video/<int:video_pk>/delete/', views.video_delete, name='video_delete'),
    path('video_confirmation/<int:video_pk>', views.video_confirmation, name='video_confirmation'),
]
