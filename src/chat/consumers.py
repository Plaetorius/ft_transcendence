# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from users.models import BlockedUser
from django.contrib.auth import get_user_model


User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_id = f"chat_{self.room_id}" # TODO Sanitize, no more than 100 char and alphanurmeric + hypens

        await self.channel_layer.group_add(self.room_group_id, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_id, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        if not message.strip():
            return 
        user = self.scope["user"]
        if user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_id,
                {
                    "type": "chat.message",
                    "message": message,
                    "username": user.username,
                    "profile_picture": user.profile_picture.url
                }
            )
        else:
            # Shouldn't happen lol the view is @login_required
            pass
        # The special "type" key turns the . in _, thus "chat.message"
        # corresponds to chat_message() (function above)

    async def chat_message(self, event):
        user = self.scope["user"]
        if await self.is_user_blocked(user.username, event["username"]):
            return
        username = event["username"]
        message = event["message"]
        profile_picture = event["profile_picture"]
        await self.send(text_data = json.dumps({"message": message, "username": username, "profile_picture": profile_picture}))

    @database_sync_to_async
    def is_user_blocked(self, scope_username, event_username):
        try:
            scope_user = User.objects.get(username=scope_username)
        except User.DoesNotExist:
            return True
        try:
            event_user = User.objects.get(username=event_username)
        except User.DoesNotExist:
            return True
        return BlockedUser.objects.filter(blocked=event_user, blocker=scope_user).exists()
