# chat/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import models
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import (
    ChatRoom,
    Message,
)

def roomView(request, username):
    return render(request, "chat/chat.html")
