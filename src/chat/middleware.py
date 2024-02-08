from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()

class TokenAuthMiddleware(BaseMiddleware):
    """
    Custom token auth middleware for Django Channels 3
    """

    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        # Get query string for URL
        query_string = parse_qs(scope['query_string'].decode())
        # Get token from query string
        token = query_string.get('token')

        # If no token has been found, set user to AnonymousUser
        if not token:
            scope['user'] = AnonymousUser()
        # Else, retrieve user from token and set scope['user'] to it
        else:
            user = await self.get_user_from_token(token[0])
            scope['user'] = user

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            # Decode the token
            access_token = AccessToken(token)
            # Retrieve the user
            user = User.objects.get(id=access_token["user_id"])
            return user
        except Exception as e:
            return AnonymousUser()
