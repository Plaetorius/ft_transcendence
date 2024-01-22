# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import async_to_sync

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
        message = event["message"]
        username = event["username"]
        profile_picture = event["profile_picture"]
        await self.send(text_data = json.dumps({"message": message, "username": username, "profile_picture": profile_picture}))
