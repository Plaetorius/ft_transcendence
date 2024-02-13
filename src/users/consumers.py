# users/comsummers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone   
from .models import User

class UserStatus(AsyncWebsocketConsumer):
    async def connect(self):
        print("User got connected but the programme crashed")
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            await self.accept()
            await self.update_user_status(True)

    async def disconnect(self, close_code):
        await self.update_user_status(False)
    
    @database_sync_to_async
    def update_user_status(self, is_online):
        if self.user.is_authenticated:
            print("User authenticated")
            self.user.is_online = is_online
            self.user.last_seen = timezone.now()
            self.user.save()
        else:
            print("Not authenticated")