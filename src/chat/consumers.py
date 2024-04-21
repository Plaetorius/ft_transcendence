# chat/comsummers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.html import escape
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from users.models import BlockedUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.authenticate_user() # To identify via HTTP-Only Cookies

        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Retrieve the room to check membership
        room = await self.get_room(self.room_id)

        if isinstance(self.scope['user'], AnonymousUser) or room is None:
            # Refuse the connection if user not authenticated or room does not exist
            await self.close()
        else:
            # Check if the user is a member of the room
            if await self.is_member_of_room(room, self.scope['user']):
                # Join room group if user is authenticated and a member of the room
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()
            else:
                # Close the connection if the user is not a member of the room
                await self.close()

    @database_sync_to_async
    def get_room(self, room_id):
        try:
            return ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def is_member_of_room(self, room, user):
        return room.members.filter(id=user.id).exists()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        safe_message = escape(message)

        if (safe_message != "/clash"):
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

    @database_sync_to_async
    def authenticate_user(self):
        token = self.scope["cookies"].get("access_token")
        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token["user_id"]
                self.scope["user"] = User.objects.get(id=user_id)
            except (InvalidToken, TokenError, User.DoesNotExist):
                self.scope["user"] = AnonymousUser()