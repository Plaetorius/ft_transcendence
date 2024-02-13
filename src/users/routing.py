# users/routing.py
from django.urls import path
from .consumers import UserStatus

websocket_urlpatterns = [
    path('ws/user-status/', UserStatus.as_asgi()),
]