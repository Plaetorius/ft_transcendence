# users/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import async_to_sync

class FriendRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        self.user_group_name = f"user_{self.username}"

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def friend_request_accepted(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event["message"]))

    async def receive(self, text_data):
       pass
        # Process incoming message