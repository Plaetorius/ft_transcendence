# users/urls.py
from django.urls import path
from django.contrib.auth.views import LoginView
from .views import (
    UserProfileView,
    UserRegistrationAPIView,
	UserLoginAPIView,
	UserSearchAPIView,
)

urlpatterns = [
    path('profile/<int:pk>/', UserProfileView.as_view(), name="user-profile"),
    path('register/', UserRegistrationAPIView.as_view(), name="register-api"),
	path('login/', UserLoginAPIView.as_view(), name="login-api"),
	path('search/<str:username>/', UserSearchAPIView.as_view(), name="search-api"),
]