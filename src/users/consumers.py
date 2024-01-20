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
        event["message"] = "Requete recue ouuuuu"
        message = {"message": "Request has been received"}
        await self.send(text_data=json.dumps(message))

    async def receive(self, text_data):
       pass
        # Process incoming message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}" # TODO Sanitize, no more than 100 char and alphanurmeric + hypens

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )
        # The special "type" key turns the . in _, thus "chat.message"
        # corresponds to chat_message() (function above)

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data = json.dumps({"message": message}))
