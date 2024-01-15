from django.urls import path
from .views import user_profile_view, register_view, settings_view, login_view, all_view

urlpatterns = [
    path('profile/<str:username>/', user_profile_view, name='user_profile'),
    path('register/', register_view, name='register'),
    path('settings/', settings_view, name='settings'),
    path('login/', login_view, name='login'),
    path('all/', all_view, name='all')
]