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
    send_friend_request_view,
    delete_friend_request,
)

urlpatterns = [
    path('profile/<str:username>/', user_profile_view, name='user_profile'),
    path('register/', register_view, name='register'),
    path('settings/', settings_view, name='settings'),
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('all/', all_view, name='all'),
    path('friendships/', friendships_view, name='friendships'),
    path('user/<int:user_id>/send_friend_request/', send_friend_request_view, name='send_friend_request'),
    path('delete_friend_request/<int:request_id>', delete_friend_request, name='delete_friend_request') # TODO maybe add consistency between send and delete
]