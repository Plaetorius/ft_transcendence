# users/comsummers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone   
from .models import User
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
 


class UserNotification(AsyncWebsocketConsumer):
    """
        UserNotification class serves both as a detector to see
        if someone is online or not and also to send notifications
        to the client.
    """
    async def connect(self):
        await self.authenticate_user() # To identify via HTTP-Only Cookies

        self.user = self.scope["user"]
        if isinstance(self.scope['user'], AnonymousUser):
            await self.close()
        if self.user.is_authenticated:
            self.room_group_name = f'user_notification_{self.user.id}'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name,
            )
            await self.channel_layer.group_add("global_notification", self.channel_name)
            
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
        await self.channel_layer.group_discard("global_notification", self.channel_name)

    @database_sync_to_async
    def update_user_status(self, is_online):
        if self.user.is_authenticated:
            self.user.is_online = is_online
            self.user.last_seen = timezone.now()
            self.user.save(update_fields=['is_online', 'last_seen'])

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
