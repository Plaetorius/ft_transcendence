from django.urls import path
from .views import (
    chat_view,
    room_view,
)

urlpatterns = [
    path('', chat_view, name='chat'),
    path('<str:room_name>/', room_view, name="room")
]