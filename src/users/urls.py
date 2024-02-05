# users/urls.py
from django.urls import path
from django.contrib.auth.views import LoginView
from .views import (
    UserProfileView,
    UserRegistrationAPIView,
	UserLoginAPIView,
	UserSearchAPIView,
    UserProfileAPIView,
	UserFriendsAPIView,
    UserAddFriendAPIView,
    UserRemoveFriendAPIView,
    UserBlockAPIView,
    UserUnblockAPIView,
)

urlpatterns = [
    path('profile/<int:pk>/', UserProfileView.as_view(), name="user-profile-api"),
    path('register/', UserRegistrationAPIView.as_view(), name="register-api"),
	path('login/', UserLoginAPIView.as_view(), name="login-api"),
	path('search/<str:username>/', UserSearchAPIView.as_view(), name="search-api"),
    path('profile/', UserProfileAPIView.as_view(), name="profile-api"),
    path('friends/<str:username>/', UserFriendsAPIView.as_view(), name="friends-api"),
    path('add-friend/<str:username>', UserAddFriendAPIView.as_view(), name="add-friend-api"),
    path('remove-friend/<str:username>', UserRemoveFriendAPIView.as_view(), name="remove-friend-api"),
    path('block/<str:username>', UserBlockAPIView.as_view(), name="block-api"),
    path('unblock/<str:username>', UserUnblockAPIView.as_view(), name="unblock-api"),
]