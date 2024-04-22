# chat/views.py
from django.shortcuts import render, redirect, get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from users.authentication import CookieJWTAuthentication
from .serializers import (
    MessageSerializer,
    MembersSerializer,
)
from .models import (
    ChatRoom,
    Message,
)

User = get_user_model()

class RoomId(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        sender = request.user

        if sender.username == username:
            return Response(
                {
                    'error': 'Cannot create or access a room with yourself'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            receiver = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {
                    'error': 'User not found'
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        chatrooms = ChatRoom.objects.filter(members=sender, is_direct_message=True).filter(members=receiver)
        if chatrooms.exists():
            chatroom = chatrooms.first()
            return Response(
                {
                    'success': 'Room found',
                    'room_id': chatroom.id,
                },
                status=status.HTTP_200_OK,
            )

        if sender != receiver:
            chatroom = ChatRoom.objects.create(is_direct_message=True)
            chatroom.members.add(sender, receiver)
            return Response(
                {
                    'success': 'Room created',
                    'room_id': chatroom.id,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    'error': 'Cannot create a room with yourself'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

class RoomMessages(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        """
        GET on Messages
        """
        # Try to get the room from room_id
        try:
            room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return Response(
                {
                    'error': f"Room {room_id} doesn't exist",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the current user is a member of the room
        if not room.members.filter(id=request.user.id).exists():
            return Response(
                {
                    'error': "You do not have permission to view messages in this room",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get messages from the room
        messages = Message.objects.filter(room=room)
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(
            {
                'success': "Messages retrieved",
                'messages': serializer.data,
            },
            status=status.HTTP_200_OK,
        )

class RoomMembers(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        """
            GET method on RoomMembers, retrieves the members of a ChatRoom and returns them
            
            Parameters:
            self: a class instance of API View
            request: the calling request
            room_id: the ID of the ChatRoom in the Database
            
            Returns:
            Error:
                User.DoesNotExist:
                    Response object, error message and HTTP error 404
            Success:
                Response object, success message, members serialized, HTTP success 200 

        """
        try:
            room = ChatRoom.objects.get(id=room_id, is_direct_message=True)
        except ChatRoom.DoesNotExist:
            return Response(
                {
                    'error': f"Room {room_id} doesn't exist",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        members = room.members
        serializer = MembersSerializer(members, many=True)
        return Response(
            {
                'success': f"Members retrieved",
                'members': serializer.data,
            },
            status=status.HTTP_200_OK,
        )