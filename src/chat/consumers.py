# chat/comsummers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # TODO check if authenticated
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Join room group
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

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': self.scope['user'].id,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']

        await self.save_message(sender_id, self.room_id, message)

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': await self.get_username(sender_id),
        }))

    @database_sync_to_async
    def save_message(self, sender_id, room_id, message):
        print(f"Room ID {room_id}")
        sender = User.objects.get(id=sender_id)
        room = ChatRoom.objects.get(id=room_id)
        return Message.objects.create(room=room,sender=sender, content=message)

    @database_sync_to_async
    def get_username(self, user_id):
        try:
            user = User.objects.get(id=user_id).username
            return user
        except User.DoesNotExist:
            return None
            