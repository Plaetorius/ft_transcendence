# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from .models import User, Friendship, BlockedUser
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.files.base import ContentFile
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
	UserLoginSerializer,
    FriendshipSerializer,
    BlockedUserSerializer,
    UserAllSerializer,
    UserUpdateSerializer,
)
import requests
import os

# TODO Don't forget to escape bio before rendering it

def send_user_notification(user_id, text_message: str, path_to_icon: str, context: dict):
    """
        send_user_notification()
        Input:
            - user_id: int; the id of the user that will receive the notification
            - text_message: str; message to display in notification
            - path_to_icon: str; url to the icon to display in notification
            - context: dict; additional useful information (button, link for it, HTML...)
    """
    channel_layer = get_channel_layer()
    group_name = f'user_notification_{user_id}'
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'user.notification',
            'text_message': text_message,
            'path_to_icon': path_to_icon,
            'context': context,
        }
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


# TODO cleaner code, reduce boilerplate code
class UserFriendAPIView(APIView):
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
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

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
        # If friends, delete Friendship, return success
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

class UserBlockAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        # Get request user
        blocker = request.user
        # Try get username user
        try:
            blocked = User.objects.get(username=username)
        # Exception if doesn't exist
        except User.DoesNotExist:
            return Response(
                {'error': "User doesn't exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Check if trying to block himself
        if blocker == blocked:
            return Response(
                {'error': "You can't block yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Check if not already blocked (WARNING: blocking is 1-sided)
        if BlockedUser.objects.filter(blocker=blocker, blocked=blocked).exists():
            return Response(
                {'error': "You already blocked this user!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Block user, return success + created
        serializer = BlockedUserSerializer(
            data={
                'blocker_id': blocker.id,
                'blocked_id': blocked.id,
            }
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'success': f'Successfully blocked {username}'},
                status=status.HTTP_201_CREATED,
            )
        # Return error + bad request
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, username):
        # Get request user
        blocker = request.user
        # Try get username user
        try:
            blocked = User.objects.get(username=username)
        # Exception if doesn't exist
        except User.DoesNotExist:
            return Response(
                {'error': "User doesn't exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Check if trying to unblock himself
        if blocker == blocked:
            return Response(
                {'error': "You can't unblock yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Get block
        block = BlockedUser.objects.filter(blocker=blocker, blocked=blocked)
        # If exists, delete, return success
        if (block.exists()):
            block.delete()
            return Response(
                {'success': f"Successfully unblocked {username}"},
                status=status.HTTP_200_OK,
            )
        # If not, return error
        return Response(
            {'error': "You haven't blocked that person"},
            status=status.HTTP_400_BAD_REQUEST,
        )

class UserListBlockedAPIView(APIView):
    permissions_classes = [IsAuthenticated]

    def get(self, request):
        """
            Returns the list of users blocked by the request user
        """
        blocker = request.user
        blocked_list = []
        blocked_queryset = BlockedUser.objects.filter(blocker=blocker)
        for blocked in blocked_queryset:
            blocked_list.append(blocked.blocked.username)
        return Response(
            {
                'success': "Blocked user list found",
                'list': blocked_list,
            },
            status=status.HTTP_200_OK,
        )

class UserEditAPIView(APIView):
    permissions_classes = [IsAuthenticated]

    def get(self, request):
        """
            Returns all the data (even sensitive) from the user emitting the request
        """
        serializer = UserAllSerializer(request.user)
        return Response(
            {
                "success": "Retrieved all user data",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    # TODO add sanitization
    def put(self, request):
        """
            Updates the user's information
        """
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": "Profile updated",
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "error": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

class OAuthCallbackView(View):
    def get(self, request, *args, **kwargs):
        code = request.GET.get('code', '')
        if not code:
            return JsonResponse({'error': 'Missing code'}, status=status.HTTP_400_BAD_REQUEST)
        
        CLIENT_ID = os.environ.get('42_CLIENT_ID')
        CLIENT_SECRET = os.environ.get('42_CLIENT_SECRET')
        REDIRECT_URI = 'https://localhost/users/oauth2/callback'
        
        # Exchange code for access token
        response = requests.post(
            'https://api.intra.42.fr/oauth/token',
            data={
                'grant_type': 'authorization_code',
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'code': code,
                'redirect_uri': REDIRECT_URI,
            },
        )
        
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to retrieve access token'}, status=response.status_code)
        
        access_token_data = response.json()
        access_token = access_token_data['access_token']
        
        # Fetch user data from 42's API using the access token
        user_response = requests.get('https://api.intra.42.fr/v2/me', headers={'Authorization': f'Bearer {access_token}'})
        
        if user_response.status_code != 200:
            return JsonResponse({'error': 'Failed to retrieve user data'}, status=user_response.status_code)
        
        user_data = user_response.json()
        print(user_data)

        username = user_data['login']
        email = user_data['email']
        first_name = user_data['first_name']
        last_name = user_data['last_name']
        profile_picture_url = user_data['image']['link']
        
        # Download the profile picture
        profile_picture_response = requests.get(profile_picture_url)
        if profile_picture_response.status_code == 200:
            # Convert the downloaded image to a Django File
            profile_picture_file = ContentFile(profile_picture_response.content)
            
            # Check if user exists, create or update accordingly
            user, created = User.objects.get_or_create(username=username)
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.oauth = True
            
            # Set the profile picture
            user.profile_picture.save(f"{username}_profile.jpg", profile_picture_file, save=True)
            user.save()
        
        return JsonResponse({'success': 'User authenticated', 'username': username}, status=status.HTTP_200_OK)