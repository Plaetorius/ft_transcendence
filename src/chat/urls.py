# chat/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from channels.routing import ProtocolTypeRouter, URLRouter
from .consumers import ChatConsumer
from .views import (
    getId,
)


application =  ProtocolTypeRouter({
    'websocket': URLRouter([
        path('ws/chat/<str:username>/', ChatConsumer.as_asgi()),
    ]),
})


urlpatterns = [
    path('get-id/<str:username>/', getId.as_view(), name="getId"),
]