from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import UserRegistrationForm, UserSettingsForm

def user_profile_view(request, username):
    user = User.objects.get(username=username)
    return render(request, 'users/profile.html', {'user': user})

def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, "users/register.html", {'form': form})

@login_required
def settings_view(request):   
    user = request.user
    if request.method == "POST":
        form = UserSettingsForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('settings')
            # return render(request, 'users/settings.html', {'user': user, 'form': form})
    else:
        form = UserSettingsForm(instance=user)
    return render(request, 'users/settings.html', {'user': user, 'form': form})


def login_view(request):
    return render(request, 'users/login.html')
    