# users/urls.py
from django.urls import path
from django.contrib.auth.views import LoginView
from .views import (
    user_profile_view,
    register_view,
    settings_view,
    login_view,
    all_view,
    friendships_view,
    send_friend_request,
    friend_request_accept,
    friend_request_refuse,
    friendship_remove,
)

urlpatterns = [
    path('profile/<str:username>/', user_profile_view, name='user_profile'),
    path('register/', register_view, name='register'),
    path('settings/', settings_view, name='settings'),
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('all/', all_view, name='all'),
    path('friendships/', friendships_view, name='friendships'),
    path('send_friend_request/', send_friend_request, name='send_friend_request'),
    path('friend_request_accept/<int:request_id>/', friend_request_accept, name='friend_request_accept'),
    path('friend_request_refuse/<int:request_id>/', friend_request_refuse, name='friend_request_refuse'),
    path('friendship_remove/<int:friendship_id>/', friendship_remove, name='friendship_remove'),
]