# chat/comsummers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from users.models import BlockedUser

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # TODO check if authenticated
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        if isinstance(self.scope['user'], AnonymousUser):
            # Refuse the connection if user not atuthenticated
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
        print(event)
        # if not sender_id:
        #     sender_id = self.scope['user'].id
        print(f"Sender id from event: {sender_id}")

        await self.save_message(sender_id, self.room_id, message)

        # Check if message is from blocked user
        if await self.is_sender_blocked(sender_id=sender_id):
            return

        username = await self.get_username(sender_id)
        if not username:
            return
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': username,
        }))

    @database_sync_to_async
    def save_message(self, sender_id, room_id, message):
        print(f"Sender ID={sender_id}")
        sender = User.objects.get(id=sender_id)
        room = ChatRoom.objects.get(id=room_id)
        return Message.objects.create(room=room, sender=sender, content=message)

    @database_sync_to_async
    def get_username(self, user_id):
        try:
            user = User.objects.get(id=user_id).username
            return user
        except User.DoesNotExist:
            return None
    
    @database_sync_to_async
    def is_sender_blocked(self, sender_id):
        try:
            room = ChatRoom.objects.get(id=self.room_id, is_direct_message=True)
            members = room.members.all()
            # FIXME doesn't work for room with 2+ ppl
            for member in members:
                if BlockedUser.objects.filter(blocker=member, blocked__id=sender_id).exists():
                    return True
            return False
        # Really unlikely
        except ChatRoom.DoesNotExist:
            print(f"Chatroom {self.room_id} doesn't exist")
            return True