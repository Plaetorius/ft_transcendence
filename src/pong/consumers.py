# consumers.py

from typing import List

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser

import json
import uuid
import asyncio
import random
import time
import math

from django.contrib.auth.models import ( AbstractUser )
from django.contrib.auth import get_user_model
User = get_user_model()

from .classes.player import Player
from .classes.party import Party

# GAME CLASSES
from .game_classes.pong_game import PongParty
from .game_classes.pong_tournament import pongTournament


##
##	CLASS PARTY MANAGER
##

class SmallParty():
	def __init__(self, *args, **kwargs):
		self.uuid: str						= str(uuid.uuid4())
		self.name: str						= f"party_default"
		self.players: List[Player]			= []
		self.max_players: int				= 2

	def to_dict(self):
		return {
			"uuid": self.uuid,
			"name": self.name,
			"players": [player.to_dict() for player in self.players],
			"max_players": self.max_players
		}

class PartyManager():
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.parties: dict[str, Party]				= {}
		self.small_parties: dict[str, SmallParty]	= {}
		self.in_games: dict[str, Party]				= {}
		self.channel_layer							= get_channel_layer()
		self.create_party("bot", pongTournament())

	def create_party(self, name: str, party_type = None) -> Party:
		if party_type == None:
			party_type = PongParty()
		party = party_type
		party.name = party.name + f"_{name}"
		self.parties[party.uuid] = party
		print(f"####	PartyManager: Party {party.uuid} created")
		
		self.small_parties[party.uuid] = SmallParty()
		self.small_parties[party.uuid].uuid = party.uuid
		self.small_parties[party.uuid].name = party.name
		self.small_parties[party.uuid].max_players = party.max_players

		return party
	
	async def delete_party(self, party_uuid: str) -> bool:
		if party_uuid in self.parties:
			self.parties[party_uuid].game_stop()

			del self.parties[party_uuid]
			del self.small_parties[party_uuid]

			print(f"####	PartyManager: Party {party_uuid} deleted")
			return True
		return False


	async def join_party(self, party_uuid: str, player: Player) -> bool:
		# Check if the player is already in a game
		if (self.in_games.get(player.id, None) != None):
			print(f"####	PartyManager: Player {player.name} cannot join the party (player already in a game)")
			return False

		# Check if the party exists
		party = self.parties.get(party_uuid, None)
		if party == None:
			print(f"####	PartyManager: Player {player.name} could not join party {party_uuid} (party not found)")
			return False
		small_party = self.small_parties.get(party_uuid, None)

		# Try to join the party
		success = party.game_join(player)
		if (success == True):
			# update fast access dictionnary (not accessed in real time party loop)
			small_party.players.append(player)

			# update fast access dictionnary for player in game (not accessed in real time party loop)
			self.in_games[player.id] = player

			# start_game handle error cases by itself
			await self.start_game(party_uuid)

			return True

		return False

	async def leave_party(self, party_uuid: str, pl: Player) -> bool:
		# Check if the player is not in a game
		player = self.in_games.get(pl.id, None)
		
		if (player == None):
			return False

		# Check if the party exists
		party = self.parties.get(party_uuid, None)
		if party == None:
			print(f"####	PartyManager: Player {player.name} could not leave party {party_uuid} (party not found)")
			return False
		small_party = self.small_parties[party_uuid]

		# Try to leave the party
		success = party.game_leave(player)
		if (success == True):
			small_party.players.remove(player)
			del self.in_games[player.id]
			self.parties[party_uuid].game_leave(player)
			return True
		
		print(f"####	PartyManager: Player {player.name} could not leave party {party_uuid} (party not found)")
		return False

	async def start_game(self, party_uuid: str) -> bool:
		if party_uuid in self.parties:
			return self.parties[party_uuid].game_start()
		print(f"####	PartyManager: Could not start game for party {party_uuid} (party not found)")
		return False
	
	async def stop_game(self, party_uuid: str) -> bool:
		if party_uuid in self.parties:
			return self.parties[party_uuid].game_stop()
		print(f"####	PartyManager: Could not stop game for party {party_uuid} (party not found)")
		return False
	
	def to_dict(self):
		return {
			"parties": [party.to_dict() for party in self.parties.values()]
	}
	
	def real_time_dict(self):
		return {
			"parties": [party.real_time_dict() for party in self.parties.values()]
	}


# PARTY MANAGER SINGLETON
g_party_manager: PartyManager	= PartyManager()



# PARTY CONSUMER
class PartyConsumer(AsyncWebsocketConsumer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def connect(self):
		# Init channel values
		self.party_uuid: str			= self.scope['url_route']['kwargs']['party_uuid']
		self.party: Party				= None
		# self.user						= await self.get_user(self.scope['user'].username)
		self.party_channel_name: str	= f"party_{self.party_uuid}"
		self.player: Player				= None
		self.obj_to_remove: list[str]	= []
		
		await self.authenticate_user() # To identify via HTTP-Only Cookies

		self.user = self.scope["user"]
		if isinstance(self.scope['user'], AnonymousUser):
			await self.close()
			return

		# Check if party exists and if player can join
		if (self.party_uuid not in g_party_manager.parties):
			print(f"####	PartyConsumer: Could not connect to party:{self.party_uuid} (party not found)")
			await self.close()
			return
	
		if (g_party_manager.in_games.get(self.user.id, None) != None):
			print(f"####	PartyConsumer: Could not connect to party:{self.party_uuid} (player already in a game)")
			await self.close()
			return
		
		# Check if player can join the party and join it
		self.player = Player(self.user.username, self.user.id)
		if (await g_party_manager.join_party(self.party_uuid, self.player) == False):
			await self.close()
			return
		
		self.party = g_party_manager.parties[self.party_uuid]
		
		# If everything is ok, connect to the party
		print(f"####	PartyConsumer: Connect to channel {self.party_channel_name} (party:{self.party_uuid})")
		await self.channel_layer.group_add(self.party_channel_name, self.channel_name)
		
		# Accept connection
		await self.accept()


	async def disconnect(self, close_code):
		print(f"####	PartyConsumer: ERROR CODE: {close_code}")
		await self.channel_layer.group_discard(self.party_channel_name, self.channel_name)

		if (self.player == None):
			return
		await g_party_manager.leave_party(self.party_uuid, self.player)
		print(f"####	PartyConsumer: Disconnect from channel {self.party_channel_name} (party:{self.party_uuid})")

	# Receive message from WebSocket
	async def receive(self, text_data):
		# print(f"####	PartyConsumer: message received: {text_data}")
		text_data_json = json.loads(text_data)
		
		try:
			await self.party._game_receive(text_data_json)
		except Exception as e:
			print(f"####	PartyConsumer: ERROR: {e}")


	# Send message to all players in the party
	async def party_update(self, event):
		
		# Send message to all players in the party
		message = {
				"type": "update",
				"party": self.party.real_time_dict()
			}

		# Add the obj to the remove buffer
		if (event.get('obj_to_remove', None) != None):
			self.obj_to_remove.extend(event['obj_to_remove'])
		
		# Add obj_to_remove to the message
		message["party"]['obj_to_remove'] = self.obj_to_remove

		try:
			await self.send(text_data=json.dumps(message))
		except Exception as e:
			print(f"####	PartyConsumer: ERROR: {e}")

	async def party_title(self, event):

		# Kick player not allowed to see the message
		if (not self.player.id in event['players']):
			return
		
		message = {
			'type': 'title',
			'text': event['text'],
			'img': event['img'],
			'time': event['time'],
		}

		print("Sending title message")
		print(message)

		try:
			await self.send(text_data=json.dumps(message))
		except Exception as e:
			print(f"####	PartyConsumer: ERROR: {e}")

	async def party_disconnect(self, event):
		if (self.player == None):
			return
		if (event['player_id'] == self.player.id):
			print(f"####	PartyConsumer: Player {self.player.name} disconnected from party {self.party_uuid}")
			await self.close()

	@database_sync_to_async
	def get_user(self, field: str) -> User:
		return User.objects.get(username=field)

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
