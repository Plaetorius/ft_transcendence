# chat/urls.py
from django.urls import path
from .views import (
    chat_view,
    room_view,
)

urlpatterns = [
    path('', chat_view, name='chat'),
    path('<int:room_id>/', room_view, name="room")
]