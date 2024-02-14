# users/routing.py
from django.urls import re_path
from .consumers import (
    UserStatus,
)

websocket_urlpatterns = [
    re_path(r"ws/user-status/$", UserStatus.as_asgi()),
]