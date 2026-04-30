
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('<int:user_id>/', views.chat_room, name='chat_room'),
    path('send/', views.send_message, name='send_message'),
    path('poll/<int:user_id>/', views.poll_messages, name='poll_messages'),
    path('unread/', views.unread_count, name='unread_count'),
]
