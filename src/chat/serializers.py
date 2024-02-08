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

class MembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'profile_picture_url')
    
    def get_profile_picture_url(self, obj):
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return obj.profile_picture.url
        return None