# chat/urls.py
from django.urls import path
from .views import (
    chat_view,
    room_view,
    message_user,
)

urlpatterns = [
    path('', chat_view, name='chat'),
    path('rooms/<int:room_id>/', room_view, name="room"),
    path('message_user/<int:user_id>', message_user, name="message_user"),
]