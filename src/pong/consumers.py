# consumers.py

from typing import List

import json
import uuid
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import random


from django.contrib.auth.models import ( AbstractUser )
from django.contrib.auth import get_user_model
User = get_user_model()

from .classes.player import Player

from .classes.objects import ObjectAbstract, Shape

##
##	CLASS PARTY
##

# PARTY CONSUMER
class Party():
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.uuid: str				= str(uuid.uuid4())
		self.name: str				= f"party_default" # To display in the frontend
		self.players: List[Player]	= []
		self.max_players: int		= 1
		self.started: bool			= False
		self.is_public: bool		= True
		self.party_channel_name: str= f"party_{self.uuid}"
		self.objects: List[ObjectAbstract]	= []

		# for i in range(2):
		# 	baisetamere = ObjectAbstract()
		# 	self.objects.append(baisetamere)

	def to_dict(self):
		return {
			"uuid": self.uuid,
			"name": self.name,
			"players": [player.to_dict() for player in self.players],
			"max_players": self.max_players,
			"started": self.started,
			"is_public": self.is_public,
			"party_channel_name": self.party_channel_name,
			"objects": [obj.to_dict() for obj in self.objects]
		}


##
##	CLASS PARTY MANAGER
##

class PartyManager():
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.parties: dict[str, Party]	= {}
		self.in_games: dict[str, Party]	= {}
		self.channel_layer = get_channel_layer()
	
	def create_party(self, name: str) -> Party:
		party = Party()
		party.name = f"{name}"
		self.parties[party.uuid] = party
		print(f"####	PartyManager: Party {party.uuid} created")
		return party
	
	def delete_party(self, party_uuid: str) -> bool:
		if party_uuid in self.parties:
			del self.parties[party_uuid]
			print(f"####	PartyManager: Party {party_uuid} deleted")
			return True
		return False
	
	
	def join_party(self, party_uuid: str, player: Player) -> bool:
		if (self.in_games.get(player.id, None) != None):
			print(f"####	PartyManager: Player {player.name} cannot join a game (player already in a game)")
			return False
		party = self.parties.get(party_uuid, None)
		if party != None:
			temp_list_id = [player.id for player in party.players]
			print(f"####	PartyManager: Party {party_uuid} has {len(party.players)} and i am {player.id} players:")
			for p in temp_list_id:
				print(f"####	-{p}")
			if player.id not in temp_list_id:
				if len(party.players) < party.max_players:
					party.players.append(player)
					print(f"####	PartyManager: Player {player.name} joined party {party_uuid}")
					self.in_games[player.id] = player
					# start_game handle error cases by itself
					# await self.channel_layer.group_send(party.party_channel_name, {"type": "update_party"})
					self.start_game(party_uuid)
					return True
				else:
					print(f"####	PartyManager: Player {player.name} could not join party {party_uuid} (party full)")
					return False
			else:
				print(f"####	PartyManager: Player {player.name} could not join party {party_uuid} (player already in party n°{party_uuid})")
				return False
		print(f"####	PartyManager: Player {player.name} could not join party {party_uuid} (party not found)")
		return False

	def leave_party(self, party_uuid: str, player: Player) -> bool:
		if (self.in_games.get(player.id, None) == None):
			print(f"####	PartyManager: Player {player.name} cannot leave a game (player not in a game)")
			return False
		if party_uuid in self.parties:
			party = self.parties[party_uuid]
			
			temp_player = next((p for p in party.players if p.id == player.id), None)
			
			if temp_player != None:
				del self.in_games[player.id]		# Remove player from the playing list
				party.players.remove(temp_player)	# Remove player from the party
				print(f"####	PartyManager: Player {player.name} left party {party_uuid}")
				print(f"####	PartyManager: Party {party_uuid} has {len(party.players)} players")
				return True
			
			print(f"####	PartyManager: Player {player.name} could not leave party {party_uuid} (player not found)")
			return False
		print(f"####	PartyManager: Player {player.name} could not leave party {party_uuid} (party not found)")
		return False
	
	def start_game(self, party_uuid: str) -> bool:
		if party_uuid in self.parties:
			party = self.parties[party_uuid]
			if (party.started == True):
				print(f"####	PartyManager: Could not start game for party {party_uuid} (game already started)")
				return False
			if len(party.players) == party.max_players:
				print(f"####	PartyManager: Starting game for party {party_uuid}")
				party.started = True
				party.objects = [ObjectAbstract() for i in range(3)]
				party.objects[0].pos.y = 250 - (16 / 2)		#taille de la map en y - taille du paddle / 2
				party.objects[1].pos.y = -250 + (16 / 2)	#taille de la map en y + taille du paddle / 2
				party.objects[2].shape = Shape.SPHERE
				return True
			else:
				print(f"####	PartyManager: Could not start game for party {party_uuid} (not enough players)")
				return False
		print(f"####	PartyManager: Could not start game for party {party_uuid} (party not found)")
		return False
	
	def stop_game(self, party_uuid: str) -> bool:
		if party_uuid in self.parties:
			party = self.parties[party_uuid]
			if party.started == True:
				print(f"####	PartyManager: Stopping game for party {party_uuid}")
				return True
			else:
				print(f"####	ParyManager: Could not stop game for party {party_uuid} (game not started)")
				return False
		print(f"####	PartyManager: Could not stop game for party {party_uuid} (party not found)")
		return False
	
	def to_dict(self):
		return {
			"parties": [value.to_dict() for key, value in self.parties.items()]
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
		temp_player = Player(self.user.username, self.user.id)
		if (g_party_manager.join_party(self.party_uuid, temp_player) == False):
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
		# if (g_party_manager.in_games.get(self.user.id, None) != None):
		# 	return
		player_to_remove = Player(self.user.username, self.user.id)
		g_party_manager.leave_party(self.party_uuid, player_to_remove)
		print(f"####	PartyConsumer: Disconnect from channel {self.party_channel_name} (party:{self.party_uuid})")
	

	# Receive message from WebSocket
	async def receive(self, text_data):
		# print(f"####	PartyConsumer: message received: {text_data}")
		text_data_json = json.loads(text_data)
		
		if (text_data_json['type'] == "update"):	
			
			for obj in self.party.objects:
				if obj.shape == Shape.PADDLE:
					if obj.controler != None: # todo != None
						#print(f"keys = {text_data_json['keys']} AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
						#if obj.controler.id == self.user.id:
						if text_data_json['keys'].get("q", False) == True: # or "ArrowLeft"
							obj.pos.x -= 10
						if text_data_json['keys'].get("d", False) == True: # or "ArrowRight"
							obj.pos.x += 10
						if text_data_json['keys'].get("p", False) == True: 
							obj.pos.y = random.uniform(-1, 1) * 220
							obj.pos.x = random.uniform(-1, 1) * 50
				else:
					obj.pos.y += random.uniform(-1, 1)
					obj.pos.x += random.uniform(-1, 1)

			message = {
				"type": "update",
				"party": self.party.to_dict(),
				"color": "0x00FF00",
			}
			await self.send(text_data=json.dumps(message))

	async def update_party(self, event):
		# Send message to all players in the party
		await self.channel_layer.group_send( self.party_channel_name, {self.party.to_dict()} )
	
	@database_sync_to_async
	def get_user(self, field: str) -> User:
		return User.objects.get(username=field)

	# async def join_party(self, event):
	# 	party_uuid = event['party_uuid']
	# 	await self.channel_layer.group_send(
	# 		f"party_{party_uuid}",
	# 		{
	# 			"type": "user_join",
	# 			"user_channel_name": self.party_channel_name
	# 		}
	# 	)

# #
# #	GAMELOBBY MANAGER
# #

# # GAMELOBBYCONSUMER
# class GameLobbyConsumer(AsyncWebsocketConsumer):
# 	async def connect(self):
# 		await self.accept()
# 		await self.channel_layer.group_add("game_lobby", self.channel_name)
# 		await self.send_json({"message": "You have entered the game lobby."})

# 	async def disconnect(self, close_code):
# 		await self.channel_layer.group_discard("game_lobby", self.channel_name)

# 	async def join_party(self, event):
# 		party_uuid = event['party_uuid']
# 		await self.channel_layer.group_send(
# 			f"party_{party_uuid}",
# 			{
# 				"type": "user_join",
# 				"user_channel_name": self.channel_name
# 			}
# 		)

# 	async def leave_party(self, event):
# 		party_uuid = event['party_uuid']
# 		await self.channel_layer.group_send(
# 			f"party_{party_uuid}",
# 			{
# 				"type": "user_leave",
# 				"user_channel_name": self.channel_name
# 			}
# 		)

# 	async def user_joined(self, event):
# 		user_channel_name = event['user_channel_name']
# 		await self.send_json({"message": f"User {user_channel_name} joined the party."})

# 	async def user_left(self, event):
# 		user_channel_name = event['user_channel_name']
# 		await self.send_json({"message": f"User {user_channel_name} left the party."})
