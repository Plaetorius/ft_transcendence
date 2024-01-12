from django.urls import path
from .views import user_profile_view, register

urlpatterns = [
    path('profile/<str:username>/', user_profile_view, name='user_profile'),
    path('register/', register, name='register'),
]