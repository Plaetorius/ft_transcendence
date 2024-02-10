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
    sender_username = serializers.SerializerMethodField()
    sender_pp_url = serializers.SerializerMethodField()

    class Meta:
        model = Message
        # TODO can be optimized if list of members is kept client side on chat room entering
        fields = ('id', 'room', 'content', 'timestamp', 'sender_username', 'sender_pp_url')

    def get_sender_username(self, obj):
        return obj.sender.username
    
    def get_sender_pp_url(self, obj):
        request = self.context.get('request')
        if obj.sender.profile_picture and hasattr(obj.sender.profile_picture, 'url'):
            return obj.sender.profile_picture.url
            # TODO is it best to? return request.build_absolute_uri(obj.sender.profile_picture.url)
        return None


class MembersSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'profile_picture_url')
    
    def get_profile_picture_url(self, obj):
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return obj.profile_picture.url
        return None