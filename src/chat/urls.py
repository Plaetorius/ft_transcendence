# chat/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from channels.routing import ProtocolTypeRouter, URLRouter
from .consumers import ChatConsumer
from .views import (
    roomView,
)


application =  ProtocolTypeRouter({
    'websocket': URLRouter([
        path('ws/chat/<str:username>/', ChatConsumer.as_asgi()),
    ]),
})


urlpatterns = [
    # path('', include(router.urls)),
    # path('<str:username>/', roomView, name="room-view"),
]