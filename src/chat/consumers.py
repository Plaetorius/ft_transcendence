# chat/comsummers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # TODO check if authenticated
        user = self.scope['user']
        print(f"URL route: {self.scope['url_route']}")
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # Retrieve sender from scope
        sender = self.scope['user']
        # Try getting receiver from 
        # try:

#         user = self.scope['user'] 
#         print(f"\
# Path: {self.scope['path']}\n\
# Headers: {self.scope['headers']}\n\
# URL Route: {self.scope['url_route']}\n\
#             ")
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))