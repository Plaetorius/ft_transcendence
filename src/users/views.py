from django.shortcuts import render
from .models import User

def user_profile_view(request, username):
    user = User.objects.get(username=username)
    return render(request, 'users/profile.html', {'user': user})