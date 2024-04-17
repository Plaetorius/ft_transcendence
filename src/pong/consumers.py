# consumers.py

from typing import List

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import json
import uuid
import asyncio
import random
import time
import math

from django.contrib.auth.models import ( AbstractUser )
from django.contrib.auth import get_user_model
User = get_user_model()

from threading import Thread, Lock

from enum import Enum

from .classes.player import Player
from .classes.objects import Shape, ObjectAbstract, ObjectTerrain, ObjectPaddle, ObjectBall
from .classes.math_vec2 import vec2

def get_time_millis():
	return int(round(time.time() * 1000))

##
##	CLASS PARTY
##

# COLLISIONS CODE
class Hit(Enum):
	NO_HIT = 0
	IN_BOUND = 1
	OUT_BOUND = 2

def collide_ray_to_box(ray_start, ray_dir, box_pos, box_size) -> tuple[Hit, float]:
	''' Return: type of collision (NO_HIT, IN_BOUND, OUT_BOUND), t (float)(infinite if no hit) '''
	t1 = (ray_start - box_pos - (box_size / 2)) / ray_dir # calculate lower bound of intersection
	t2 = (ray_start - box_pos + (box_size / 2)) / ray_dir # calculate upper bound of intersection
	
	# get the min offset percentage to reach the box border
	tmin = math.max(math.min(t1.x, t2.x), math.min(t1.y, t2.y))
	tmax = math.min(math.max(t1.x, t2.x), math.max(t1.y, t2.y))
	
	# check where the box as been hit
	if (tmin > tmax):
		return Hit.NO_HIT, math.inf
	if (tmin < 0):
		return Hit.IN_BOUND, tmax
	return Hit.OUT_BOUND, tmin

def collide_box_to_box(obj1, obj2):
	
	pass

def collide_objects(objects: list[ObjectAbstract]):
	for obj1 in objects:
		if (obj1.collide):
			for obj2 in objects:
				if (obj1 != obj2 and obj2.collide):
					
					pass
				

# PARTY CONSUMER
class Party():
	def __init__(self, *args, **kwargs):
		self.uuid: str						= str(uuid.uuid4())
		self.name: str						= f"party_default" # To display in the frontend
		self.players: List[Player]			= []
		self.max_players: int				= 4
		self.running: bool					= False
		self.is_public: bool				= True
		self.party_channel_name: str		= f"party_{self.uuid}"
		self.channel_layer					= get_channel_layer()
		self.objects: List[ObjectAbstract]	= []

		self.S_PER_UPDATE					= 1.0 / 30.0

		self._received_data: dict			= {}
		self.received_data: dict			= {}

		self.thread: Thread					= None
		self.thread_error: bool				= False

		# Add a terrain object
		terrain = ObjectTerrain()
		self.objects.append(terrain)

		for i in range(10):
			ball = ObjectBall()
			self.objects.append(ball)

	def game_start(self) -> bool:
		if (self.running == False):
			print(f"####	Party: Starting party {self.uuid}")
			self.running = True
			self.thread = Thread(target=self._game_loop)
			self.thread.start()
			return True
		else:
			print(f"####	Party: Could not start party {self.uuid} (already started)")
			return False

	def game_stop(self) -> bool:
		if self.running == True:
			print(f"####	Party: Stopping party {self.uuid} THREAD ...")
			self.running = False
			if (self.thread_error == False):
				self.thread.join()
			print(f"####	Party: Party stopped {self.uuid} THREAD !")
			return True
		else:
			print(f"####	Party: Could not stop party {self.uuid} (game not started)")
			return False

	def game_join(self, player: Player) -> bool:
		if (self.running == True and 0):
			print(f"####	Party: Player {player.name} could not join the party {self.uuid} (game already started)")
			return False
		if (any(p.id == player.id for p in self.players)):
			print(f"####	Party: Player {player.name} could not join the party {self.uuid} (player already in the party)")
			return False
		if len(self.players) < self.max_players:
			self.players.append(player)
			print(f"####	Party: Player {player.name} joined the party {self.uuid}")
			return True
		print(f"####	Party: Player {player.name} could not join the party {self.uuid} (party full)")
		return False

	def game_leave(self, player: Player) -> bool:
		if (any(p.id == player.id for p in self.players)):
			print(f"####	Party: Player {player.name} left party {self.uuid}")
			self.players.remove(player)
			if (len(self.players) == 0 and self.running == True):
				print(f"####	Party: Stopping party {self.uuid} (no more players)")
				self.game_stop()
			return True
		print(f"####	Party: Player {player.name} could not leave party {self.uuid} (player not in the party)")
		return False

	async def _game_receive(self, data):
		rdata = data.get('player_name', None)
		if (rdata != None):
			self._received_data[rdata] = data['keys']

	def _game_loop(self):
		print(f"####	Party: THREAD STARTED for party {self.uuid} at {time.time()}")

		loop_end_tick = time.time() + self.S_PER_UPDATE
		loop_offset = 0

		while self.running:

			# Update received data and clear it's buffer
			self.received_data = self._received_data.copy()
			
			# Game loop
			self.game_loop()
			
			# Send update to all players
			try:
				async_to_sync(self.channel_layer.group_send)(self.party_channel_name, {"type": "update_party"}) # Send update to all players
			except Exception as e:
				print(f"####	Party: ERROR: {e}")
				
				self.thread_error = True
				self.game_stop()
				
				return

			# print(f"####	Party: Game loop for party {self.uuid} updated at {time.time()}")
			# Update loop values
			loop_offset = loop_end_tick - time.time()
			loop_end_tick = loop_end_tick + self.S_PER_UPDATE

			# Sleep until next loop to unload CPU
			if loop_offset > 0:
				time.sleep(loop_offset)

		self.thread_error = False

	def game_loop(self):
		# Get current time
		actual_time = time.time()

		# Update objects
		collide_objects(self.objects)			

		# Update objects
		for obj in self.objects:
			obj.update()
			
		# Control objects with received data
		for obj in self.objects:
			for rkey, rvalue in self.received_data.items():
				if (obj.controler == rkey):
					obj.control(rvalue)


	def to_dict(self):
		return {
			"uuid": self.uuid,
			"name": self.name,
			"players": [player.to_dict() for player in self.players],
			"max_players": self.max_players,
			"objects": [obj.to_dict() for obj in self.objects]
		}
	
	def real_time_dict(self):
		return {
			"players": [player.to_dict() for player in self.players],
			"objects": [obj.to_dict() for obj in self.objects]
		}


##
##	CLASS PARTY MANAGER
##

class SmallParty():
	def __init__(self, *args, **kwargs):
		self.uuid: str						= str(uuid.uuid4())
		self.name: str						= f"party_default"
		self.players: List[Player]			= []
		self.max_players: int				= 4

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
	
	def create_party(self, name: str) -> Party:
		party = Party()
		party.name = f"{name}"
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

			# Add a temp object to the party
			party.objects.append(ObjectPaddle(player.name))

			# start_game handle error cases by itself
			await self.start_game(party_uuid)

			return True

		return False

	async def leave_party(self, party_uuid: str, player: Player) -> bool:
		# Check if the player is not in a game
		if (self.in_games.get(player.id, None) == None):
			print(f"####	PartyManager: Player {player.name} cannot leave a game (player not in a game)")
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
		self.user						= await self.get_user(self.scope['user'].username)
		self.party_channel_name: str	= f"party_{self.party_uuid}"
		self.player: Player				= None
		
		# Check if party exists and if player can join
		if (self.party_uuid not in g_party_manager.parties):
			print(f"####	PartyConsumer: Could not connect to party:{self.party_uuid} (party not found)")
			await self.close(code=99900)
			return
	
		if (g_party_manager.in_games.get(self.user.id, None) != None):
			print(f"####	PartyConsumer: Could not connect to party:{self.party_uuid} (player already in a game)")
			await self.close(code=99902)
			return
		
		# Check if player can join the party and join it
		self.player = Player(self.user.username, self.user.id)
		if (await g_party_manager.join_party(self.party_uuid, self.player) == False):
			await self.close(code=99901)
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

	async def update_party(self, event):

		# Send message to all players in the party
		message = {
				"type": "update",
				"party": self.party.real_time_dict()
			}
	
		try:
			await self.send(text_data=json.dumps(message))
		except Exception as e:
			print(f"####	PartyConsumer: ERROR: {e}")
	
	@database_sync_to_async
	def get_user(self, field: str) -> User:
		return User.objects.get(username=field)
