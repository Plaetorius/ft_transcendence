# chat/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import ChatRoom
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def chat_view(request):
    return render(request, 'chat/chat.html')

@login_required
def room_view(request, room_id):
    user = request.user
    room_id = int(room_id)
    try:
        print("Room exists")
        room = ChatRoom.objects.get(id=room_id)
    except ChatRoom.DoesNotExist:
        print("Room doesn't exist")
        second_user = User.objects.get(username="dumb")
        room = ChatRoom.objects.create(user1=user, user2=second_user)
        return render(request, 'chat/room.html', {'room_id': room.id, 'user': user})
    print(request.path)
    return render(request, 'chat/room.html', {'room_id': room_id, 'user': user})