# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Friendship, FriendRequest
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
    
@login_required
def all_view(request):
    users = User.objects.all
    return render(request, 'users/all.html', {'users': users})

@login_required
def friendships_view(request):
    user = request.user
    friendships = Friendship.objects.filter(user=user) | Friendship.objects.filter(friend=user)
    return render(request, 'users/friendships.html', {'user': user, 'friendships': friendships})

@login_required
def add_friendship_view(request, user_id): 
    if request.method == "POST":
        friend_username = request.POST.get('friend_username')
        user = User.objects.get(id=user_id)
        friend = User.objects.get(username=friend_username)
        if friend:
            Friendship.objects.create(user=user, friend=friend)
    friendships = Friendship.objects.filter(user=user) | Friendship.objects.filter(friend=user)
    return render(request, 'users/friendships.html', {'user': user, 'friendships:': friendships, 'requests:': requests})

@login_required
def send_friend_request_view(request, user_id):
    if request.method == "POST":
        friend_username = request.POST.get('friend_username')
        user = User.objects.get(id=user_id)
        friend = User.objects.get(username=friend_username)
        if friend:
            FriendRequest.objects.create(from_user=user, to_user=friend)
            messages.success(request, 'Your request has been successfully sent!')
            # TODO Check if to_user has blocked from_user
    friendships = Friendship.objects.filter(user=user) | Friendship.objects.filter(friend=user)
    friend_requests = FriendRequest.objects.filter(to_user=user) | FriendRequest.objects.filter(from_user=user)
    return render(request, 'users/friendships.html', {'user': user, 'friendships': friendships, 'friend_requests': friend_requests})

@login_required
def delete_friend_request(request, request_id):
    user = request.user
    friend_request = FriendRequest.objects.get(id=request_id)
    friendships = Friendship.objects.filter(user=user) | Friendship.objects.filter(friend=user)
    friend_requests = FriendRequest.objects.filter(to_user=user) | FriendRequest.objects.filter(from_user=user)
    if not friend_request:
        messages.failure("This request doesn't exist")
        return render(request, 'users/friendships.html', {'user': user, 'friendships': friendships, 'friend_requests': friend_request})     
    if user != friend_request.to_user and user != friend_request.from_user:
        messages.failure("Can't delete that friendship request")
        return render(request, 'users/friendships.html', {'user': user, 'friendships': friendships, 'friend_requests': friend_request})
    