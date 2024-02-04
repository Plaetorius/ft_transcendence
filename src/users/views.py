# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Friendship, FriendRequest, BlockedUser
from .forms import UserRegistrationForm, UserSettingsForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
	UserLoginSerializer,
    FriendshipSerializer,
)

class UserProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserRegistrationAPIView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            res_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(res_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginAPIView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data,
        }, status=status.HTTP_200_OK)

class UserSearchAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

class UserProfileAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=request.user.id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

class UserFriendsAPIView(generics.RetrieveAPIView):
	serializer_class = UserSerializer
	permission_classes = [IsAuthenticated]

	def get(self, request, *args, **kwargs):
		user = get_object_or_404(User, id=request.user.id)
		serializer = self.get_serializer(user)
		return Response(serializer.data)

class UserAddFriendAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        # Get request user
        user = get_object_or_404(User, id=request.user.id)
        # Try get username user
        try:
            friend = User.objects.get(username=username)
        # Exception if doesn't exist
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND,
                )
        # Check if user adding himself as friend
        if user == friend:
            return Response(
                {'error': "You can't add yourself as a friend!"},
                status=status.HTTP_400_BAD_REQUEST, 
            )
        # Check if not already friends
        if Friendship.objects.filter(friend1=user, friend2=friend).exists() or Friendship.objects.filter(friend1=friend, friend2=user).exists():
            return Response(
                {'error': "You're already friends!"},
                status=status.HTTP_400_BAD_REQUEST,
            )   
        # Validate data with serializer
        serializer = FriendshipSerializer(
            data={
                'friend1_id': user.id,
                'friend2_id': friend.id
                }
            )
        # Create Friendship
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'success': "Friend added."},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            # {'error': 'Serializer error'},
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserRemoveFriendAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, username):
        # Get request user
        user = request.user
        # Try get username user
        try:
            friend = User.objects.get(username=username)
        # Exception if doesn't exist
        except User.DoesNotExist:
            return Response(
                {'error': "User doesn't exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Check if trying to remove himself (useless but cleaner)
        if user == friend:
            return Response(
                {'error': "You can't unfriend yourself, have some self love <3"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Check if friends
        friendship = Friendship.objects.filter(friend1=user, friend2=friend) | Friendship.objects.filter(friend1=friend, friend2=user)
        # If friends, remove Friendship, return success
        if friendship.exists():
            friendship.delete()
            return Response(
                {'success': "Friend removed."},
                status=status.HTTP_200_OK,
            )
        # Else, return error
        return Response(
            {'error': "You're not friend with that person"},
            status=status.HTTP_400_BAD_REQUEST,
        )


def user_profile_view(request, username):
    # TODO can be upgraded to have better support if a user isn't found
    user = get_object_or_404(User, username=username)
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
    emitted_friend_requests = FriendRequest.objects.filter(from_user=user)
    received_friend_requests = FriendRequest.objects.filter(to_user=user)
    blocked = BlockedUser.objects.filter(blocker=user)
    blocked_by = BlockedUser.objects.filter(blocked=user)
    context = {
        'user': user,
        'friendships': friendships,
        'emitted_friend_requests': emitted_friend_requests,
        'received_friend_requests': received_friend_requests,
        'blocked': blocked,
        'blocked_by': blocked_by,
        }
    return render(request, 'users/friendships.html', context)

@login_required
def send_friend_request(request):
    user = request.user
    if request.method == "POST":
        friend_username = request.POST.get('friend_username')
        if friend_username == user.username:
            messages.error(request, "You cannot have yourself as a friend. Touch some grass!")
            return redirect('friendships')
        try:
            friend = User.objects.get(username=friend_username)
            if Friendship.objects.filter(user=user, friend=friend).exists() or \
               Friendship.objects.filter(user=friend, friend=user).exists():
                messages.error(request, "You are already friends.")
                return redirect('friendships')
            if FriendRequest.objects.filter(from_user=user, to_user=friend).exists() or \
               FriendRequest.objects.filter(from_user=friend, to_user=user):
                messages.error(request, "You already have a friend request pending")
                return redirect('friendships')
            
            # Optional: Check if the user is blocked
            # if BlockedUser.objects.filter(blocker=friend, blocked=user).exists():
            #     messages.error(request, "This user has blocked you.")
            #     return redirect('some_view')

            FriendRequest.objects.create(from_user=user, to_user=friend)
            messages.success(request, 'You have successfully sent a friend request')
        except User.DoesNotExist:
            messages.error(request, "The user doesn't exist")
    return redirect('friendships')

@login_required
def friendship_remove(request, friendship_id):
    """
    Remove a friend
    """
    friendship = None
    try:
        friendship = Friendship.objects.get(id=friendship_id)
    except Friendship.DoesNotExist:
        return redirect('friendships')
    if not (request.user == friendship.user or request.user == friendship.friend):
        messages.error(request, "Not friend with that person") # TODO remove
        return redirect('friendships')
    friendship.delete()
    messages.success(request, "Friend removed!")
    return redirect('friendships')

@login_required
def friend_request_accept(request, request_id):
    """
    Received friend request acceptation
    """
    friend_request = None
    try:
        friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
    except FriendRequest.DoesNotExist:
        messages.error(request, "No such friend request found")
        return redirect('friendships')
    Friendship.objects.create(user=request.user, friend=friend_request.from_user)
    friend_request.delete()
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{request.user.username}",
        {
            "type": "friend_request_accepted",
            "message": {
                "friend_username": request.user.username
            }
        }
    )
    messages.success(request, "Friend added!")
    return redirect('friendships')

@login_required
def friend_request_refuse(request, request_id):
    """
    Sent friend request cancellation and received friend request denyal
    """
    friend_request = None
    try:
        friend_request = FriendRequest.objects.get(id=request_id, from_user=request.user)
    except FriendRequest.DoesNotExist:
        try:
            friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
        except FriendRequest.DoesNotExist:
            pass
    if not friend_request:
        messages.error(request, "No such friend request found.")
        return redirect('friendships')
    friend_request.delete()
    messages.success(request, "Friend request deleted.")
    return redirect('friendships')

@login_required
def block_user(request, user_id):
    user = request.user
    try:
        to_block = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User does not exist")
        return redirect('friendships')
    if to_block == user:
        messages.error(request, "You can't block yourself!")
        return redirect('friendships')
    BlockedUser.objects.create(blocker=user, blocked=to_block)
    #TODO maybe remove friendship
    return redirect('friendships')

@login_required 
def unblock_user(request, user_id):
    user = request.user
    try:
        to_unblock = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User does not exist")
        return redirect('friendships')
    if to_unblock == user:
        messages.error(request, "You can't unblock yourself!")
        return redirect('friendships')
    try:
        block_elem = BlockedUser.objects.get(blocker=user, blocked=to_unblock)
    except BlockedUser.DoesNotExist:
        messages.error(request, "You haven't blocked that user")
        return redirect('friendships')
    block_elem.delete()
    return redirect('friendships')

@login_required
def pipboy_view(request, profile_id):
	try:
		profile_user = User.objects.get(id=profile_id)
	except User.DoesNotExist:
		messages.error(request, "User doesn't exist!")
		return redirect("friendships")
	return render(request, 'users/pipboy.html', {})
	