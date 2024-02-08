# chat/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from channels.routing import ProtocolTypeRouter, URLRouter
from .consumers import ChatConsumer
from .views import (
    RoomId,
    RoomMessages,
    RoomMembers,
)


application =  ProtocolTypeRouter({
    'websocket': URLRouter([
        path('ws/chat/<str:username>/', ChatConsumer.as_asgi()),
    ]),
})


urlpatterns = [
    path('room-id/<str:username>/', RoomId.as_view(), name="room-id"),
    path('room-messages/<int:room_id>/', RoomMessages.as_view(), name="room-messages"),
    path('room-members/<int:room_id>/', RoomMembers.as_view(), name="room-members"),
]