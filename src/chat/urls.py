# chat/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    roomView,
)

router = DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    path('<str:username>/', roomView, name="room-view"),
]