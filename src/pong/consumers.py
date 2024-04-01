from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

import logging

from .includes import ( party_room, Player )

class PongConsumer(AsyncWebsocketConsumer):
	
	async def connect(self):
		# Called when the WebSocket is handshaking as part of the connection process
		channel_user = self.scope['user']
		
		logging.critical("Connected")
		logging.critical("CHAN_USR: " + str(channel_user))
		
		temp_player = Player(channel_user.username, channel_user.id)
		
		party_room.add_player(temp_player)
		# debug
		logging.critical(temp_player)
		
		await self.accept()

	async def disconnect(self, close_code):
		# Called when the WebSocket closes for any reason
		logging.critical("Disconnected")
		
		temp_player = party_room.get_players_by_id(self.channel_name)

	async def receive(self, text_data):
		# Called when the consumer receives data over the WebSocket
		logging.critical("Received")
		logging.critical(text_data)