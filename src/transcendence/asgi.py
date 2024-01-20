# asgi.py
import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path
from users.consumers import FriendRequestConsumer
from users.routing import websocket_urlpatterns
from django.urls import re_path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "transcendence.settings")

django_asgi_app = get_asgi_application()

import users.routing

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter([
#             re_path(r'^ws/friend-requests/(?P<username>\w+)/$', FriendRequestConsumer.as_asgi()),
#         ])
#     ),
# })
