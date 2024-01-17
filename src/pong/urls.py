# pong/urls.py
from django.urls import path
from .views import (
    games_view,
)

urlpatterns = [
    path('games/', games_view, name="pong_games")
]