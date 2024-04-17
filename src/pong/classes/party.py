
from typing import List

from .player import Player
from .objects import ( ObjectAbstract, Shape, ObjectTerrain, ObjectBall )
from .math_vec2 import vec2

from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import uuid
import random
import time
import math

from threading import Thread, Lock

from enum import Enum

from .player import Player
from .objects import Shape, ObjectAbstract, ObjectTerrain, ObjectPaddle, ObjectBall
from .math_vec2 import vec2

#
# COLLISIONS CODE
#

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

#
# CLASS PARTY
#

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
		
		pass

	########################
	# User defined methods #
	########################
 
	def	_game_start(self) -> bool:
		return True

	def	_game_stop(self) -> bool:
		return True

	def	_game_loop(self) -> bool:
		return True
	
	def	_game_join(self, player: Player) -> bool:
		return True
	
	def	_game_leave(self, player: Player) -> bool:
		return True
	
	def _game_send_update(self):
		return True
	
	####################
	# NO TOUCH methods #
	####################

	def game_start(self) -> bool:
		if (self.running == False):
			print(f"####	Party: Starting party {self.uuid} ...")
			
			# Call custom _game_start method
			if (self._game_start() == False):
				print(f"####	Party: Could not start party {self.uuid} (game_start failed)")
				return False
			
			self.running = True
			self.thread = Thread(target=self.game_loop)
			self.thread.start()
			
			print(f"####	Party: Party started {self.uuid}")
			return True
		else:
			print(f"####	Party: Could not start party {self.uuid} (already started)")
			return False

	def game_stop(self) -> bool:
		if self.running == True:
			
			# Call custom _game_stop method
			if (self._game_stop() == False):
				print(f"####	Party: Could not stop party {self.uuid} (game_stop failed)")
				return False
			print(f"####	Party: Party stopped {self.uuid}")
			
			# try:
			# 	async_to_sync(self.channel_layer.group_send)(self.party_channel_name, {"type": "party_stopped"}) # Send update to all players
			# except Exception as e:
			# 	print(f"####	Party: ERROR: {e}")
			
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
			print(f"####	Party: Player {player.name} could not join party {self.uuid} (game already started)")
			return False
		if (any(p.id == player.id for p in self.players)):
			print(f"####	Party: Player {player.name} could not join party {self.uuid} (player already in party)")
			return False
		if len(self.players) < self.max_players:
			print(f"####	Party: Player {player.name} is joining party {self.uuid}")
			
			# Call custom _game_join method
			if (self._game_join(player) == False):
				print(f"####	Party: Player {player.name} could not join party {self.uuid} (game_join failed)")
				return False
			
			self.players.append(player)
			print(f"####	Party: Player {player.name} joined party {self.uuid}")
			return True
		print(f"####	Party: Player {player.name} could not join party {self.uuid} (party full)")
		return False

	def game_leave(self, player: Player) -> bool:
		if (any(p.id == player.id for p in self.players)):
			print(f"####	Party: Player {player.name} is leaving party {self.uuid}")
			
			# Call custom _game_leave method
			if (self._game_leave(player) == False):
				print(f"####	Party: Player {player.name} could not leave party {self.uuid} (game_leave failed)")
				return False
		
			self.players.remove(player)
			
			if (len(self.players) == 0 and self.running == True):
				print(f"####	Party: Stopping party {self.uuid} (no more players)")
				self.game_stop()

			return True
		print(f"####	Party: Player {player.name} could not leave party {self.uuid} (player not in party)")
		return False

	async def _game_receive(self, data):
		rdata = data.get('player_name', None)
		if (rdata != None):
			self._received_data[rdata] = data['keys']

	def game_loop(self):
		print(f"####	Party: THREAD STARTED for party {self.uuid} at {time.time()}")

		loop_end_tick = time.time() + self.S_PER_UPDATE
		loop_offset = 0

		while self.running:

			# Update received data and clear it's buffer
			self.received_data = self._received_data.copy()
			
			
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
			
			# Run custom _game_loop
			if (self._game_loop() == False):
				self.game_stop()
				return
			
			print(f"####	Party: Looping party {self.uuid} at {time.time()} ...")
			
			# Send update to all players
			try:
				async_to_sync(self.channel_layer.group_send)(self.party_channel_name, {"type": "update_party"}) # Send update to all players
			except Exception as e:
				print(f"####	Party: ERROR: {e}")
				
				self.thread_error = True
				self.game_stop()
				
				return

			# Update loop values
			loop_offset = loop_end_tick - time.time()
			loop_end_tick = loop_end_tick + self.S_PER_UPDATE

			# Sleep until next loop to unload CPU
			if loop_offset > 0:
				time.sleep(loop_offset)

		self.thread_error = False

	def to_dict(self):
		return {
			"uuid": self.uuid,
			"name": self.name,
			"players": [player.to_dict() for player in self.players],
			"max_players": self.max_players,
			"objects": [obj.to_dict() for obj in self.objects],
			"second_per_frames": self.S_PER_UPDATE,
		}
	
	def real_time_dict(self):
		return {
			"players": [player.to_dict() for player in self.players],
			"objects": [obj.to_dict() for obj in self.objects],
			"second_per_frames": self.S_PER_UPDATE,
		}