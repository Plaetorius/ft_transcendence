
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
from .objects import Shape, Collision, ObjectAbstract, ObjectTerrain, ObjectPaddle, ObjectBall
from .math_vec2 import vec2

#
# COLLISIONS CODE
#

class Hit(Enum):
	NO_HIT = 0
	IN_BOUND = 1
	OUT_BOUND = 2

def collide_ray_to_box(ray_pos: vec2, ray_dir: vec2, box_pos: vec2, box_size: vec2) -> tuple[Hit, float]:
	''' Return: type of collision (NO_HIT, IN_BOUND, OUT_BOUND), t (float)(infinite if no hit) '''
	
	# Check if the ray is not a point
	if (ray_dir.x == 0 and ray_dir.y == 0):
		return Hit.NO_HIT, math.inf

	# Calculate the potentials intersection of the ray with the box
	t1 = vec2(0.0, 0.0)
	t2 = vec2(0.0, 0.0)
	if (ray_dir.x != 0):
		t1.x = (box_pos.x - (box_size.x / 2) - ray_pos.x) / ray_dir.x # calculate lower bound of intersection
		t2.x = (box_pos.x + (box_size.x / 2) - ray_pos.x) / ray_dir.x
	else:
		t1.x = (box_pos.x - (box_size.x / 2) - ray_pos.x) * 999999.0
		t2.x = (box_pos.x + (box_size.x / 2) - ray_pos.x) * 999999.0
	if (ray_dir.y != 0):
		t1.y = (box_pos.y - (box_size.y / 2) - ray_pos.y) / ray_dir.y # calculate lower bound of intersection
		t2.y = (box_pos.y + (box_size.y / 2) - ray_pos.y) / ray_dir.y
	else:
		t1.y = (box_pos.y - (box_size.y / 2) - ray_pos.y) * 999999.0
		t2.y = (box_pos.y + (box_size.y / 2) - ray_pos.y) * 999999.0
	
	# get the min offset percentage to reach the box border
	tmin = max(min(t1.x, t2.x), min(t1.y, t2.y))
	tmax = min(max(t1.x, t2.x), max(t1.y, t2.y))
	
	# check where the box as been hit
	if (tmax <= max(tmin, 0.0)):
		return Hit.NO_HIT, math.inf
	if (tmin < 0):
		return Hit.IN_BOUND, tmax
	return Hit.OUT_BOUND, tmin


def collide_box_to_box(obj1: ObjectAbstract, obj2: ObjectAbstract):
	box_size = obj1.size + obj2.size
	hit = collide_ray_to_box(obj1.pos, obj1.vel, obj2.pos, box_size)
	
	if (hit[0] != Hit.OUT_BOUND or hit[1] >= 1 or hit[1] < 0):
		return

	hit_pos = obj1.pos + obj1.vel * hit[1]
	
	normal_diff = (hit_pos - obj2.pos) / (box_size / 2)

	# Calculate the normal of the collision
	lose_vel = vec2(0.0, 0.0)
	normal = vec2(0.0, 0.0)
	if (abs(normal_diff.x) > abs(normal_diff.y)):
		lose_vel.x = obj1.vel.x
		normal.x = 1.0 if normal_diff.x >= 0 else -1.0
	else:
		lose_vel.y = obj1.vel.y
		normal.y = 1.0 if normal_diff.y >= 0 else -1.0

	# Calculate the new velocity of the object
	obj1.vel = obj1.vel - lose_vel * (1.0 - hit[1])
	
	# Calculate the new velocity of the object
	if (obj1.collide == Collision.BOUNCE):
		obj1.dir = obj1.dir + vec2(abs(obj1.dir.x), abs(obj1.dir.y)) * normal * 2
		if (obj2.controler != None and normal.y != 0.0):
			obj1.dir.x = normal_diff.x * 1.0
		obj1.dir = obj1.dir / obj1.dir.__abs__()

# TO FINE TUNE
def collide_sort_objects(objects: list[ObjectAbstract], obj1: ObjectAbstract):
	list_copy = objects.copy()
	print("before:")
	for ob in list_copy:
		print(f"{ob.uuid} {obj1.pos.distance_to(ob.pos)}")
	list_copy.sort(key=lambda obj: obj1.pos.distance_to(obj.pos), reverse=False)
	print("after:")
	for ob in list_copy:
		print(f"{ob.uuid} {obj1.pos.distance_to(ob.pos)}")
	return list_copy


def collide_objects(objects: list[ObjectAbstract]):
	for obj1 in objects:
		if (obj1.collide != Collision.NONE and obj1.collide != Collision.IMMOVABLE):
			for obj2 in objects:
				if (obj2.collide != Collision.NONE and obj1 != obj2):
					collide_box_to_box(obj1, obj2)

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

		self.objects: List[ObjectAbstract]	= []
		self.obj_to_remove: List[ObjectAbstract]	= []

		self.party_channel_name: str		= f"party_{self.uuid}"
		self.channel_layer					= get_channel_layer()
		

		self.S_PER_UPDATE					= 1.0 / 30.0
		
		self.server_tick: int				= 0

		self._received_data: dict			= {}
		self.received_data: dict			= {}

		self.thread: Thread					= None
		self.thread_error: bool				= False
		self.event_list: list[str]			= []
		
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
		try:
			if self.running == True:
				
				# Call custom _game_stop method
				if (self._game_stop() == False):
					raise Exception("game_stop failed")
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
			raise Exception("game not started")
		except Exception as e:
			print(f"####	Party: Could not stop party {self.uuid} ({e})")
			return False

	def game_join(self, player: Player) -> bool:
		try:
			if (self.running == True and 0):
				raise Exception("game already started")
			temp_player = next((p for p in self.players if p.id == player.id), None)
			if (temp_player != None):
				raise Exception("player already in party")
			if len(self.players) < self.max_players:
				print(f"####	Party: Player {player.name} is joining party {self.uuid}")				
				self.players.append(player)

				# Call custom _game_join method
				if (self._game_join(player) == False):
					self.players.remove(player)
					raise Exception("game_join failed")
				
				print(f"####	Party: Player {player.name} joined party {self.uuid}")
				return True
			raise Exception("Party is full")
		except Exception as e:
			print(f"####	Party: Player '{player.name}' could not join party {self.uuid} ({e})")
			return False
		return False

	def game_leave(self, player: Player) -> bool:
		temp_player = next((p for p in self.players if p.id == player.id), None)
		if (temp_player != None):
			print(f"####	Party: Player {temp_player.name} is leaving party {self.uuid}")
			
			# Call custom _game_leave method
			if (self._game_leave(temp_player) == False):
				print(f"####	Party: Player {temp_player.name} could not leave party {self.uuid} (game_leave failed)")
				return False
		
			self.players.remove(temp_player)
			
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


	def game_event_disconnect(self, player: Player) -> bool:
		print(f"####	Party: Event: Player {player.name} disconnecting from party {self.uuid}")
		self.event_list.append({"type": "party_disconnect", "player_id": player.id})

	def game_event_message(self, message: str, time: float,  players: list[Player] = None) -> bool:

		# Send message to all players in the party if players is None
		if (players == None):
			players = self.players

		print(f"####	Party: Event: Sending message {message}")
		print(f"####	Party: Event: Sending players {[player.id for player in players]}")

		print(f"####	Party: Event: Sending message {message} to players {[player.id for player in players]} in party {self.uuid}")
		self.event_list.append({"type": "party_title", "text": message, "time": time, "players": [player.id for player in players]})

	def game_run_event(self):
		for event in self.event_list:
			print(f"####	Party: Sending event to party {self.uuid}")
			print(f"####	Party: Sending event to party {self.party_channel_name}")
			print(f"####	Party: Sending event to party {event}")

			try:
				async_to_sync(self.channel_layer.group_send)(self.party_channel_name, event)
			except Exception as e:
				print(f"####	Party: Event: ERROR: Could not send event {event} {e}")
		self.event_list.clear()

	def game_loop(self):
		print(f"####	Party: THREAD STARTED for party {self.uuid} at {time.time()}")

		loop_end_tick = time.time() + self.S_PER_UPDATE
		loop_offset = 0

		while self.running:

			# Update received data and clear it's buffer
			self.received_data = self._received_data.copy()

			# Update objects
			for obj in self.objects:
				obj.update()
			
			# Control objects with received data
			for obj in self.objects:
				for rkey, rvalue in self.received_data.items():
					if (obj.controler == rkey):
						obj.control(rvalue)
			
			# Update objects
			collide_objects(self.objects)
			
			# Run custom _game_loop
			if (self._game_loop() == False):
				self.game_stop()
				return
			
			# print(f"####	Party: Looping party {self.uuid} at {time.time()} ...")

			# Remove objects
			for obj in self.obj_to_remove:
				if (next((o for o in self.objects if o.uuid == obj.uuid), None) != None):
					self.objects.remove(obj)
			
			# Send update to all players
			try:
				async_to_sync(self.channel_layer.group_send)(self.party_channel_name, {"type": "update_party"}) # Send update to all players
			except Exception as e:
				print(f"####	Party: ERROR: {e}")
				
				self.thread_error = True
				self.game_stop()
				
				return

			# Send update to all players
			for obj in self.obj_to_remove:
				ob = next((o for o in self.objects if o.uuid == obj.uuid), None)
				if (ob != None):
					self.objects.remove(ob)
			self.obj_to_remove.clear()

			# Run events
			self.game_run_event()

			# Update loop values
			loop_offset = loop_end_tick - time.time()
			loop_end_tick = loop_end_tick + self.S_PER_UPDATE
			
			self.server_tick = self.server_tick + 1

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
			"obj_to_remove": [obj.uuid for obj in self.obj_to_remove],
			"second_per_frames": self.S_PER_UPDATE,
		}
	
	def real_time_dict(self):
		msg = {
			"players": [player.to_dict() for player in self.players],
			"objects": [obj.to_dict() for obj in self.objects],
			"obj_to_remove": [obj.uuid for obj in self.obj_to_remove],
			"second_per_frames": self.S_PER_UPDATE,

		}
		self.obj_to_remove.clear()
		return msg