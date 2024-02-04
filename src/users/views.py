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
    BlockedUserSerializer,
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

class UserUnblockAPIView(APIView):
    permission_classes = [IsAuthenticated]

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
            {'success': "You haven't blocked that person"},
            status=status.HTTP_400_BAD_REQUEST,
        )
