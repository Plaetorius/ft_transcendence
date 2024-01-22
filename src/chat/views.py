# chat/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import ChatRoom
from django.db import models
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden

User = get_user_model()

@login_required
def chat_view(request):
    return render(request, 'chat/chat.html')

@login_required
def room_view(request, room_id):
    user = request.user
    # room_id = int(room_id)
    # try:
    room = ChatRoom.objects.get(id=room_id)
    if not room.members.filter(id=user.id).exists():
        return HttpResponseForbidden("Not a member")
    #     print(f"Room exists {room_id}")
    # except ChatRoom.DoesNotExist:
    #     print(f"Room doesn't exist {room_id}")
    #     room = ChatRoom.objects.create()
    #     print(f"Created room {room.id}")
    #     return render(request, 'chat/room.html', {'room_id': room.id, 'user': user})
    # print(request.path)
    return render(request, 'chat/room.html', {'room': room, 'room_id': room_id, 'user': user})

# Tool function
def get_direct_message(user1, user2):
    room = ChatRoom.objects.filter(
        members__in=[user1, user2],
        is_direct_message=True
    ).annotate(num_members=models.Count('members')).filter(num_members=2).first()
    # filter() and first() don't raise the DoesNotExist exception but return null 
    if room == None:
        room = ChatRoom.objects.create(is_direct_message=True)
        room.members.add(user1, user2)
    return room

@login_required
def message_user(request, user_id):
    user1 = request.user
    try:
        user2 = User.objects.get(id=user_id)
    except User.DoesNotExist:
        print("User.DoesNotExist in message_user")
        return # TODO use messages 
    room = get_direct_message(user1, user2)
    return redirect('room', room_id=room.id)
    # return render(request, "chat/room.html", {"room": room, "user1": user1, "user2": user2, "room_id": room.id})
    