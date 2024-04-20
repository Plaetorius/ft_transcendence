
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
		self.color		= '#31363F'
		self.collide	= Collision.BOUNCE
		self.pos		= vec2(0, 0)
		self.size		= vec2(8, 8)
		self.speed		= 16.0
		
		self.init_rotation()

	def init_rotation(self, rot: float = 0.0):
		self.rot = rot
		self.dir = vec2(math.sin(rot), math.cos(rot))
	
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
		
		self.is_state_on: bool			= False
		self.state_timer: float			= 0.0
		self.next_state: GameState		= GameState.STOPPED
		
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
		terrain.size = vec2(200, 200)
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
		small_border = terrain.size * 0.6
  
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
		for i in range(6):
			bababoule = PongBall()
			bababoule.init_rotation(uniform(-math.pi, math.pi))
			random_size = uniform(6, 10)
			bababoule.size = vec2(random_size, random_size)
			if (randint(0, 1) == 0):
				bababoule.pos.x = terrain.size.x * 0.9 / 2 * (1 if randint(0, 1) == 0 else -1)
				bababoule.pos.y = uniform(-0.5, 0.5) * terrain.size.y * 0.9
			else:
				bababoule.pos.x = uniform(-0.5, 0.5) * terrain.size.x * 0.9
				bababoule.pos.y = terrain.size.y * 0.9 / 2 * (1 if randint(0, 1) == 0 else -1)
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

		# Add paddle if in game lobby
		self.obj_to_remove.append(player.my_paddle)
		player.my_paddle = ObjectPaddle(player.name)
		player.my_paddle.size = vec2(16, 16)
		player.my_paddle.pos = vec2(0, 0)
		player.my_paddle.controler = player.name
		self.objects.append(player.my_paddle)

		return True

	def	_game_leave(self, player: Player) -> bool:
		return True

	# Game send update
	def _game_send_update(self):
		return True
