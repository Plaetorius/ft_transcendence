
from django.conf import settings
from channels.layers import get_channel_layer
from typing import List

import asyncio

import uuid

from .game_base import GameBase
from .player import Player

#
# CLASS PARTY
#

class Party(GameBase):
	def __init__(self):
		super().__init__()
		
		self.channel_layer = get_channel_layer()
		
		self.players = []
		self.max_players = 2
		
		self.uuid = str(uuid.uuid4())
		
		self.channel_name = f"pong_party_{self.uuid}"
		self.update_lock = asyncio.Lock()
	
	def __del__(self) -> None:
		self.players.clear()

# Player manager
	async def add_player(self, player: Player) -> bool:
		if (len(self.players) >= self.max_players):
			return False
		self.players.append(player)
		
		await self.channel_layer.group_add(
				type = self.channel_name,
				self.channel_name,
				player.id,
				)
		
		return True

	async def rem_player(self, player: Player) -> bool:
		if (len(self.players) == 0):
			return False
		self.players.remove(player)
		
		await self.channel_layer.group_discard(
				self.channel_name,
				player.id,
				)
		
		return True

	async def game_update(self, event):
		"""
		Called when someone talk to the party
		"""
		# Send a message down to the client
		await self.send_json(
			{
				"msg_type": settings.MSG_TYPE_MESSAGE,
				"room": event["room_id"],
				"username": event["username"],
				"message": event["message"],
			},
		)

	# async def loop():
	# 	pass


#
# CLASS PARTYROOM
#

class PartyRoom:
	_instance = None
	
	def __new__(cls):
		if cls._instance is None:
			cls._instance = super().__new__(cls)
		return cls._instance
	
	def __init__(self):
		self.parties = []
		self.players = []
		self.loop_running = False

# manager parties
	def add_party(self, party: Party) -> bool:
		self.parties.append(party)
		return True

	def rem_party(self, party: Party) -> bool:
		if (self.parties.count == 0):
			return False
		self.parties.remove(party)
		return True
	
	def rem_party_by_id(self, uuid: uuid) -> bool:
		party = self.get_party_by_uuid(uuid)
		error = self.rem_party(party)
		return error

#
	def get_party_by_uuid(self, party_uuid: str) -> bool:
		for party in self.parties:
			if party.uuid == party_uuid:
				return party
		return None
		
# manager players
	def	add_player(self, player: Player) -> bool:
		self.players.append(player)
		print(f"	PONGGAME: Player {player.name} has joined the party room")
		print(f"	PONGGAME: There is now {len(party_room.players)} players in the party room")
		print("INFO: list of players: " + party_room.players.__repr__())
		return True
	
	def rem_player(self, player: Player) -> bool:
		if ((player == None) or (self.players.count == 0)):
			return False
		self.players.remove(player)
		return True
	
	def rem_player_by_id(self, player_id: int) -> bool:
		player = self.get_player_by_id(player_id)
		error = self.rem_player(player)
		print(f"	PONGGAME: Player {player.name} has left the party room")
		print(f"	PONGGAME: There is now {len(party_room.players)} players in the party room")
		print("INFO: list of players: " + party_room.players.__repr__())
		return error
	
#
	def get_player_by_name(self, player_name: str) -> bool:
		for player in self.players:
			if player.name == player_name:	
				return player
		return None

	def get_player_by_id(self, player_id: int) -> bool:
		for player in self.players:
			if player.id == player_id:
				return player
		return None
	
	async def game_loop(self):
		while self.loop_running:
			# Update the game state
			# self.game_state.update()
			
			# Send updates to all connected clients
			#await self.send_game_state()

			print("	GAMEPONG: INFO: Game loop running")

			# Wait for a short interval (e.g., 20 milliseconds)
			await asyncio.sleep(0.5)
	
# global game manager
party_room = PartyRoom()
