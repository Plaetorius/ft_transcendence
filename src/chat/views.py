from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@login_required
def chat_view(request):
    return render(request, 'chat/chat.html')

@login_required
def room_view(request, room_name):
    return render(request, 'chat/room.html', {'room_name': room_name})