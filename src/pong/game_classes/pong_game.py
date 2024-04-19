
from ..classes.party import ( Party )
from ..classes.player import ( Player )
from ..classes.objects import ( Shape, Collision, ObjectAbstract, ObjectBall, ObjectTerrain, ObjectPaddle)
from ..classes.math_vec2 import ( vec2 )

from enum import Enum
from random import uniform, randint

import random, math, json, uuid, time

	#####################
	#  CLASS PONG BALL  #
	#####################

class	PongBall(ObjectAbstract):
	def	__init__(self):
		super().__init__()
		self.shape		= Shape.BALL
		self.collide	= Collision.BOUNCE
		self.size		= vec2(16, 16)
		self.speed		= 4
		
		self.init_rotation()

	def init_rotation(self, rot: float = 0.0):
		self.rot = rot
		self.dir = vec2(math.sin(rot), math.cos(rot))
		self.vel = self.dir * self.speed
	
	def	update(self):
		self.pos = self.pos + self.vel
		self.vel = self.dir * self.speed


	######################
	#  CLASS PONG PARTY  #
	######################

class	GameState(Enum):
	STOPPED		= 0
	STARTING	= 1
	PLAYING		= 2
	ENDING		= 3

class	PongParty(Party):
	def	__init__(self):
		super().__init__()
		
		# Defautl party settings
		self.name = "Pong Game"
		self.max_players = 2
		self.S_PER_UPDATE = 1.0 / 20.0
		
		# Custom party settings
		self.allowed_players: list[str]	= []
		self.game_state: GameState		= GameState.STOPPED
		
		# Change world state to STOPPED (lobby)
		self.update_world_state(GameState.STOPPED)
		
		pass
		
	def create_game_world(self):
		
		# Remove all objects
		self.obj_to_remove.extend(self.objects)
		
		# Create Terrain
		terrain = ObjectTerrain()
		self.objects.append(terrain)
		
		# Create Terrain borders
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

		# Create Ball (saved in self.game_ball)
		self.game_ball = PongBall()
		random_rot = (0.0, math.pi)[randint(0, 1)] + uniform(-0.5, 0.5) # Random direction
		self.game_ball.init_rotation(random_rot) 
		self.objects.append(self.game_ball)
		
		pass
	
	def create_game_lobby(self):
		
		# Remove all objects
		self.obj_to_remove.extend(self.objects)
		
		# Create Terrain
		terrain = ObjectTerrain()
		terrain.size = vec2(128, 128)
		self.objects.append(terrain)
		
		# Create Terrain borders
		box = ObjectAbstract()
		box.shape = Shape.BOX
		box.size = vec2(4, terrain.size.y)
		box.pos = vec2(terrain.size.x / 2, 0)
		self.objects.append(box)
		box = ObjectAbstract()
		box.shape = Shape.BOX
		box.size = vec2(4, terrain.size.y)
		box.pos = vec2(-terrain.size.x / 2, 0)
		self.objects.append(box)
		box = ObjectAbstract()
		box.shape = Shape.BOX
		box.size = vec2(terrain.size.x, 4)
		box.pos = vec2(0, terrain.size.y / 2)
		self.objects.append(box)
		box = ObjectAbstract()
		box.shape = Shape.BOX
		box.size = vec2(terrain.size.x, 4)
		box.pos = vec2(0, -terrain.size.y / 2)
		self.objects.append(box)
		
		# Create BABABOULE borders
		small_border = terrain.size * 0.8
  
		box = ObjectAbstract()
		box.shape = Shape.BOX
		box.size = vec2(4, small_border.y)
		box.pos = vec2(small_border.x / 2, 0)
		self.objects.append(box)
		box = ObjectAbstract()
		box.shape = Shape.BOX
		box.size = vec2(4, small_border.y)
		box.pos = vec2(-small_border.x / 2, 0)
		self.objects.append(box)
		box = ObjectAbstract()
		box.shape = Shape.BOX
		box.size = vec2(small_border.x, 4)
		box.pos = vec2(0, small_border.y / 2)
		self.objects.append(box)
		box = ObjectAbstract()
		box.shape = Shape.BOX
		box.size = vec2(small_border.x, 4)
		box.pos = vec2(0, -small_border.y / 2)
		self.objects.append(box)

		# Create BABABOULES
		bababoule = PongBall()
		random_rot = (0.0, math.pi)[randint(0, 1)] + uniform(-1.5, 1.5) # Random direction
		bababoule.init_rotation(random_rot) 
		bababoule.pos.x = terrain.size.x * 0.9 / 2
		bababoule.pos.y = 0.0
		bababoule.size = vec2(6, 6)
		self.objects.append(bababoule)
		bababoule = PongBall()
		random_rot = (0.0, math.pi)[randint(0, 1)] + uniform(-1.5, 1.5) # Random direction
		bababoule.init_rotation(random_rot) 
		bababoule.pos.x = 0.0
		bababoule.pos.y = -terrain.size.x * 0.9 / 2
		bababoule.size = vec2(6, 6)
		self.objects.append(bababoule)
		
		pass

	def	update_world_state(self, state: GameState):
		self.game_state = state
		if (state == GameState.STOPPED):
			self.create_game_lobby()
		elif (state == GameState.STARTING):
			self.create_game_world()

	def	_game_start(self) -> bool:
		
		return True

	def	_game_stop(self) -> bool:
		return True

	def	_game_loop(self) -> bool:
		return True
	
	def	_game_join(self, player: Player) -> bool:
		
		# Check if player is already in the game
		is_allowed = next((p for p in self.allowed_players if p == player.id), None)
		
		if (self.game_state == GameState.STOPPED):
			print(f"PONG: Player {player.id} joined the game")
		else:
			# Kick player if game is running and player is not allowed to joins
			if (is_allowed == None):
				print(f"PONG: Player {player.id} cannot join the game (player not allowed to join)")
				return False

		return True

	def	_game_leave(self, player: Player) -> bool:
		return True

	# Game send update
	def _game_send_update(self):
		return True
