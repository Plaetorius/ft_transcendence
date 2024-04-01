# asgi.py
import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path

from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from users.routing import websocket_urlpatterns as users_websocket_urlpatterns
from pong.routing import websocket_urlpatterns as pong_websocket_urlpatterns

from chat.middleware import TokenAuthMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "transcendence.settings")

django_asgi_app = get_asgi_application()

websocket_urlpatterns = chat_websocket_urlpatterns + users_websocket_urlpatterns + pong_websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            TokenAuthMiddleware(
                AuthMiddlewareStack(
                    URLRouter(
                        websocket_urlpatterns,
                    )
                )
            )
        ),
    }
)
