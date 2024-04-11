
from django.urls import re_path
from .consumers import PartyConsumer

websocket_urlpatterns = [
	re_path(r"^ws/pong/(?P<party_uuid>[^/]+)/$", PartyConsumer.as_asgi()),
]
