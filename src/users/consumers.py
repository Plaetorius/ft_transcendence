# users/comsummers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone   
from .models import User


class UserNotification(AsyncWebsocketConsumer):
    """
        UserNotification class serves both as a detector to see
        if someone is online or not and also to send notifications
        to the client.
    """
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.room_group_name = f'user_notification_{self.user.id}'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name,
            )
            await self.accept()
            await self.update_user_status(True)

    async def user_notification(self, event):
        text_message = event['text_message']
        path_to_icon = event['path_to_icon']
        context = event['context']
        await self.send(text_data=json.dumps({
            # Defines the JSON model; do not alter
            'message': text_message,
            'path_to_icon': path_to_icon,
            'context': context,
        }))

    async def disconnect(self, close_code):
        await self.update_user_status(False)
    
    @database_sync_to_async
    def update_user_status(self, is_online):
        if self.user.is_authenticated:
            self.user.is_online = is_online
            self.user.last_seen = timezone.now()
            self.user.save(update_fields=['is_online', 'last_seen'])
