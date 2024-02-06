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

from .models import (
    ChatRoom,
    Message,
)

User = get_user_model()

class getId(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        # Get request user
        sender = request.user
        print(f'Sender: {sender}, Username: {username}')
        # Try get username user
        try:
            receiver = User.objects.get(username=username)
        # Exception if doesn't exist
        except User.DoesNotExist:
            # Return error message, no ChatRoom ID and NOT FOUND HTTP Response
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Check if room exists
        chatrooms = ChatRoom.objects.filter(members=sender, is_direct_message=True).filter(members=receiver)
        if chatrooms.exists():
            # Safety
            chatroom = chatrooms.first()
            # Send the response with the ChatRoom ID and OK HTTP Response
            return Response(
                {
                    'success': 'Room found',
                    'room_id': chatroom.id,
                },
                status=status.HTTP_200_OK,
            )
        # Create the chatroom if doesn't exist
        chatroom = ChatRoom.objects.create(is_direct_message=True)
        chatroom.members.add(sender, receiver)
        # Send the response with the ChatRoom ID and creation HTTP Response
        return Response(
                {
                    'success': 'Room created',
                    'room_id': chatroom.id,
                },
                status=status.HTTP_201_CREATED,
            )