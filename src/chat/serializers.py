# chat/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    ChatRoom,
    Message,
)

User = get_user_model()

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'