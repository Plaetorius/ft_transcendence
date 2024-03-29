# chat/comsummers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.html import escape
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from users.models import BlockedUser

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        if isinstance(self.scope['user'], AnonymousUser):
            # Refuse the connection if user not authenticated
            await self.close()
        else:
            # Join room group if user is authenticated
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        safe_message = escape(message)

        # Save the message once here.
        await self.save_message(self.scope['user'].id, self.room_id, safe_message)

        # Then broadcast it to the group.
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': safe_message,
                'sender_id': self.scope['user'].id,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        safe_message = escape(message)
        sender_id = event['sender_id']

        username, profile_picture = await self.get_info(sender_id)
        if not username:
            return
        await self.send(text_data=json.dumps({
            'message': safe_message, 
            'sender': {
                'username' : username,
                'profile_picture': profile_picture,
            },
        }))

    @database_sync_to_async
    def save_message(self, sender_id, room_id, message):
        sender = User.objects.get(id=sender_id)
        room = ChatRoom.objects.get(id=room_id)
        return Message.objects.create(room=room, sender=sender, content=message)

    @database_sync_to_async
    def get_info(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            username = user.username
            profile_picture = user.profile_picture.url
            return username, profile_picture
        except User.DoesNotExist:
            return None
