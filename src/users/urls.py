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
    UserFriendAPIView,
    UserBlockAPIView,
    UserListBlockedAPIView,
    UserEditAPIView,
)

urlpatterns = [
    path('profile/<int:pk>/', UserProfileView.as_view(), name="user-profile-api"),
    path('register/', UserRegistrationAPIView.as_view(), name="register-api"),
	path('login/', UserLoginAPIView.as_view(), name="login-api"),
	path('search/<str:username>/', UserSearchAPIView.as_view(), name="search-api"),
    path('profile/', UserProfileAPIView.as_view(), name="profile-api"),
    path('friends/<str:username>/', UserFriendsAPIView.as_view(), name="friends-api"),
    path('friend/<str:username>', UserFriendAPIView.as_view(), name="friend-api"),
    path('block/<str:username>', UserBlockAPIView.as_view(), name="block-api"),
    path('list-blocked/', UserListBlockedAPIView.as_view(), name="list-blocked-api"),
    path('edit-user/', UserEditAPIView.as_view(), name="edit-user-api"),
]