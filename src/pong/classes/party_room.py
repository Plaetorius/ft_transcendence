
from django.conf import settings

from typing import List

import json
import asyncio

import uuid
import logging

from .game_base import GameBase
from .player import Player

#
# CLASS PARTY
#

class Party(GameBase):
	party_uuid:		uuid
	players:		List[Player]
	max_players:	int
	
	def __init__(self):
		self.party_uuid = uuid.uuid4()
		self.players = []
		self.max_players = 2

# Player manager
	def add_player(self, player):
		if (self.players.count >= self.max_players):
			return False
		self.players.append(player)
		return True
		
	def rem_player(self, player):
		if (self.players.count == 0):
			return False
		self.players.remove(player)
		return True


#
# CLASS PARTYROOM
#

class PartyRoom:
	_instance = None

	parties:		List[Party]
	players:		List[Player]
	game_running:	bool
	loop_task:		asyncio.Task
	
	def __new__(cls):
		if cls._instance is None:
			cls._instance = super().__new__(cls)
		return cls._instance
	
	def __init__(self):
		self.parties = []
		self.players = []
		self.game_running = False
		self.loop_task = None

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
		party = self.get_party_by_id(uuid)
		error = self.rem_party(party)
		return error

	# getter parties
	def get_party_by_id(self, party_uuid: uuid) -> bool:
		return self.parties[party_uuid]
		
# manager players
	def	add_player(self, player: Player) -> bool:
		self.players.append(player)
		return True
	
	def rem_player(self, player: Player) -> bool:
		if ((player == None) or (self.players.count == 0)):
			return False
		self.players.remove(player)
		return True
	
	def rem_player_by_id(self, player_uuid: uuid) -> bool:
		player = self.get_players_by_id(player_uuid)
		error = self.rem_player(player)
		return error
	
	# getter players
	def get_players_by_id(self, player_name: str) -> bool:
		return self.players[player_name]

	def get_players_by_id(self, player_uuid: uuid) -> bool:
		return self.players[player_uuid]
	
	
# global game manager
party_room = PartyRoom()
