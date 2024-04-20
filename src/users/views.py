# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import User, Friendship, BlockedUser, OAuthCred, MatchHistory
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from users.authentication import CookieJWTAuthentication
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
	UserLoginSerializer,
    FriendshipSerializer,
    BlockedUserSerializer,
    UserAllSerializer,
    UserUpdateSerializer,
	FriendshipDetailSerializer,
)
import requests
import os

User = get_user_model()

def create_token_response(user, status_code):
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token

    response = Response({
        'refresh': str(refresh),
        'access': str(access_token),
        'username': user.username,
        'email': user.email,
    }, status=status_code)

    response.set_cookie(
        'refresh_token',
        str(refresh),
        httponly=True,
        samesite='Lax',
        secure=True,
        max_age=3600*24*14,  # 14 days
        path='/',
    )
    response.set_cookie(
        'access_token',
        str(access_token),
        httponly=True,
        samesite='Lax',
        secure=True,
        max_age=3600*4,  # 4 hours
        path='/',
    )
    return response

class CheckSessionView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        username = request.user.get_username()
        return Response({
            'status': 'Authenticated',
            'user': username,
        })

# TODO Don't forget to escape bio before rendering it
# I think that send_user_notification is useless
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


class UserRegistrationAPIView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return create_token_response(user=user, status_code=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginAPIView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return create_token_response(user=user, status_code=status.HTTP_200_OK)

class UserSearchAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

class UserProfileAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

class UserFriendsAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        friendships = Friendship.objects.filter(Q(friend1_id=user_id) | Q(friend2_id=user_id))
        serializer = FriendshipDetailSerializer(friendships, many=True, context={'request_user': request.user})
        return Response(serializer.data)


class UserFriendAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
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
    authentication_classes = [CookieJWTAuthentication]
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
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

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

# Consistency Update not Edit
class UserEditAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

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
    
    def patch(self, request):
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

class UserPodiumAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def get(self, request, *args, **kwargs):
        # Query the top users based on their ELO scores
        top_players = User.objects.order_by('-elo')
        serializer = UserSerializer(top_players, many=True)
        return Response(serializer.data)

class OAuthCallbackView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        token_response = self.exchange_code_for_token(code)
        access_token = token_response.json().get('access_token')
        if access_token is None:
            print("Problem with the access token")
            return Response(
                {
                    "error": "Invalid API Call",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_data = self.get_user_data(access_token)

        user, created = User.objects.update_or_create(
            username=user_data['login'],
            defaults={
                'email': user_data['email'],
            }
        )

        if created:
            user.set_unusable_password()
            user.save()

        oauth_cred, _ = OAuthCred.objects.update_or_create(
            user=user,
            defaults={
                'provider': '42', 
                'uid': user_data['id'], 
                'access_token': access_token,
                'refresh_token': token_response.json().get('refresh_token'),
            }
        )
        user.oauth_cred = oauth_cred
        user.save()

        refresh = RefreshToken.for_user(user)
        res_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'email': user.email,
        }
        response = redirect('https://localhost:1026/#home')
        response.set_cookie(
            'refresh_token',
            str(refresh),
            httponly=True,
            samesite='Lax',
            secure=True,
            max_age=3600*24*14,
            path='/',
        )
        response.set_cookie(
            'access_token',
            str(refresh.access_token),
            httponly=True,
            samesite='Lax',
            secure=True,
            max_age=3600*4,
            path='/',
        )
        return response

    def exchange_code_for_token(self, code):
        token_url = 'https://api.intra.42.fr/oauth/token'
        payload = {
            'grant_type': 'authorization_code',
            'client_id': settings.OAUTH_CLIENT_ID,
            'client_secret': settings.OAUTH_CLIENT_SECRET,
            'code': code,
            'redirect_uri': settings.OAUTH_REDIRECT_URI,
        }
        return requests.post(token_url, data=payload)

    def get_user_data(self, access_token):
        user_info_url = 'https://api.intra.42.fr/v2/me'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(user_info_url, headers=headers)
        return response.json()

#TODO view for Match History, returning the matches, the W/L ratio, the rank
class UserMatchHistoryView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

