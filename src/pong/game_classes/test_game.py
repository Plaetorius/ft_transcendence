
from ..classes.party import ( Party )
from ..classes.player import ( Player )
from ..classes.objects import ( Shape, ObjectAbstract, ObjectBall, ObjectTerrain, ObjectPaddle)
from ..classes.math_vec2 import ( vec2 )

import random
import uuid
import time

class	TestParty(Party):
	def	__init__(self):
		super().__init__()
		self.name = "DEBUG MODE"
		self.max_players = 16
		
		self.S_PER_UPDATE = 1.0 / 20.0
		
		terrain = ObjectTerrain()
		self.objects.append(terrain)

		for i in range(20):
			box = ObjectAbstract()
			box.shape = Shape.BOX
			box.size = vec2(16, 16)
			box.pos = vec2(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)) * terrain.size
			self.objects.append(box)
			
		box = ObjectAbstract()
		box.shape = Shape.BOX
		box.size = vec2(terrain.size.x, 8)
		box.pos = vec2(0, terrain.size.y / 2 - 4)
		self.objects.append(box)
		
		box = ObjectAbstract()
		box.shape = Shape.BOX
		box.size = vec2(terrain.size.x, 8)
		box.pos = vec2(0, -terrain.size.y / 2 + 4)
		self.objects.append(box)
		
		box = ObjectAbstract()
		box.shape = Shape.BOX
		box.size = vec2(8, terrain.size.y)
		box.pos = vec2(terrain.size.x / 2 - 4, 0)
		self.objects.append(box)
		
		box = ObjectAbstract()
		box.shape = Shape.BOX
		box.size = vec2(8, terrain.size.y)
		box.pos = vec2(-terrain.size.x / 2 + 4, 0)
		self.objects.append(box)
		
		for i in range(30):
			ball = ObjectBall()
			ball.size = vec2(8, 8)
			self.objects.append(ball)
		
		self.object_ball = ObjectBall()

	def	_game_start(self) -> bool:
		print("PongParty: _game_start")
		return True

	def	_game_stop(self) -> bool:
		return True

	def	_game_loop(self) -> bool:
		# print(f"####	Party: Looping party {self.uuid} at {time.time()} ...")
		if (self.server_tick % 20 == 0):
			self.objects.append(self.object_ball)
		elif (self.server_tick % 20 == 10):
			self.obj_to_remove.append(self.object_ball)
		
		return True
	
	def	_game_join(self, player: Player) -> bool:
		player.paddle = ObjectPaddle(player.name)
		self.objects.append(player.paddle)
		
		return True

	def	_game_leave(self, player: Player) -> bool:
		self.obj_to_remove.append(player.paddle)
		
		return True

	def _game_send_update(self):
		return True
