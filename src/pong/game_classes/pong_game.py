
from ..classes.party import ( Party )
from ..classes.player import ( Player )
from ..classes.objects import ( Shape, Collision, ObjectAbstract, ObjectBall, ObjectTerrain, ObjectPaddle)
from ..classes.math_vec2 import ( vec2 )

from enum import Enum
from random import uniform, randint

import random, math, json, uuid, time


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

	#####################
	#  ENUM GAME STATE  #
	#####################

class	GameState(Enum):
	LOBBY		= 0
	SETTING_UP	= 1
	IN_GAME		= 2
	ENDING		= 3

	######################
	#  CLASS PONG OBJECT #
	######################

class	PongBall(ObjectAbstract):
	def	__init__(self, party: Party = None):
		super().__init__()
		self.shape		= Shape.BALL
		self.color		= '#0066b1'
		self.collide	= Collision.BOUNCE
		self.pos		= vec2(0, 0)
		self.size		= vec2(18, 18)
		self.speed		= 16.0
		self.accel		= 0.12 # Acceleration rate on bounce
		self.party		= party
		
		self.init_rotation()

	def init_rotation(self, rot: float = 0.0):
		self.rot = rot
		self.dir = vec2(math.sin(rot), math.cos(rot))
		self.vel = vec2(0, 0)
		self.old_dir = self.dir
	
	def	update(self):
		self.pos = self.pos + self.vel

		# If bounce on top or bottom
		if ((self.old_dir.y < 0 and self.dir.y >= 0) or (self.old_dir.y >= 0 and self.dir.y < 0)):
			self.speed = self.speed * (1.0 + self.accel)
			self.party.game_event_message("Ball Speed ++", 1.5, '')

		self.vel = self.dir * self.speed
		
		self.old_dir = self.dir

class PongPaddle(ObjectAbstract):
	def __init__(self, controler: str):
		super().__init__()
		self.shape		= Shape.PADDLE
		
		random.seed(controler + str(time.time()))
		r = lambda: random.randint(75, 175)
		self.color		= '#{:02x}{:02x}{:02x}'.format(r(), r(), r())
		
		self.size		= vec2(32, 23)
		self.collide	= Collision.STOP
		self.controler	= controler
		pass

	def control(self, key_values):
		val_sin = math.sin(self.rot)
		val_cos = math.cos(self.rot)

		direction = vec2(0, 0)
		if (key_values.get('a', False)):
			direction.x += +val_cos
			direction.y += -val_sin
		if (key_values.get('d', False)):
			direction.x += -val_cos
			direction.y += +val_sin

		self.vel = direction * 10
  
		pass

	def update(self):
		self.pos = self.pos + self.vel
		pass

	######################
	#  CLASS PONG PARTY  #
	######################

class	PongParty(Party):
	def	__init__(self):
		super().__init__()
		
		# Default party settings
		self.name			= "1V1 Pong"
		self.max_players	= 8
		self.S_PER_UPDATE	= 1.0 / 20.0

		# Set game to it's default state
		self.reset_game()
		
	def reset_game(self):
		# Custom party settings
		self.obj_to_remove.extend(self.objects)

		self.already_joined: dict[str]	= []
		
		self.game_state: GameState		= GameState.LOBBY
		self.next_state: GameState		= GameState.LOBBY
		self.state_timer: float			= time.time() + 999999.0

		self.old_time: int				= 0

		self.TERRAIN_SIZE: vec2			= vec2(300, 600)

		self.SCORE_MAX: int				= 5

		self.TIME_GAME_START: float		= 6.0
		self.TIME_GAME_RUN: float		= 6.0
		self.TIME_GAME_ROUND: float		= 60.0
		self.TIME_GAME_END: float		= 30.0

		self.in_game_players: list		= []
		self.in_game_ball: PongBall		= None
		self.in_game_paddles: list		= []
		
		pass
		
	def create_game_world(self):
		
		# Remove all objects
		self.obj_to_remove.extend(self.objects)
		
		# Create Terrain
		terrain = ObjectTerrain()
		terrain.size = self.TERRAIN_SIZE
		terrain.color = '#ffe1ba'
		self.objects.append(terrain)
		
		# Create Terrain borders
		box = ObjectAbstract()
		box.color = '#8b5c29'
		box.shape = Shape.BOX
		box.size = vec2(8, self.TERRAIN_SIZE.y)
		box.pos = vec2(self.TERRAIN_SIZE.x / 2 - 4, 0)
		self.objects.append(box)
		box = ObjectAbstract()
		box.color = '#8b5c29'
		box.shape = Shape.BOX
		box.size = vec2(8, self.TERRAIN_SIZE.y)
		box.pos = vec2(-self.TERRAIN_SIZE.x / 2 + 4, 0)
		self.objects.append(box)

		# Create Ball (saved in self.game_ball)
		self.in_game_ball = PongBall(self)
		random_rot = (0.0, math.pi)[randint(0, 1)] + uniform(-0.5, 0.5) # Random direction
		self.in_game_ball.init_rotation(random_rot)
		self.in_game_ball.speed = 0.0
		self.objects.append(self.in_game_ball)
		

		self.in_game_players = random.sample(self.players, 2)

		# Create IN_GAME_PLAYERS
		self.in_game_players[0].score = 0
		paddle = PongPaddle(self.in_game_players[0].name)
		paddle.size = vec2(64, 12)
		paddle.pos = vec2(0, terrain.size.y / 2 - 6)
		paddle.rot = math.pi
		self.in_game_paddles.append(paddle)

		self.in_game_players[1].score = 0
		paddle = PongPaddle(self.in_game_players[1].name)
		paddle.size = vec2(64, 12)
		paddle.pos = vec2(0, -terrain.size.y / 2 + 6)
		paddle.rot = 0.0
		self.in_game_paddles.append(paddle)

		self.objects.extend(self.in_game_paddles)

		pass
	
	def create_game_lobby(self):
		
		# Remove all objects
		self.obj_to_remove.extend(self.objects)
  
		for y in range(-2, 3):
			for x in range(-2, 3):
				dist = abs(x) + abs(y) # manhattan distance

				width = 1 + dist
				
				terrain = ObjectTerrain()
				terrain.size = vec2(width, width) * 20
				terrain.pos = vec2(x * width * 22, y * width * 22)
				terrain.color = '#ffe1ba'
				self.objects.append(terrain)

				pass
			pass
		
		border_size = vec2(600, 600)

		# Create Terrain borders
		box = ObjectAbstract()
		box.color = '#8b5c29'
		box.shape = Shape.BOX
		box.size = vec2(4, border_size.y)
		box.pos = vec2(border_size.x / 2, 0)
		self.objects.append(box)
		box = ObjectAbstract()
		box.color = '#8b5c29'
		box.shape = Shape.BOX
		box.size = vec2(4, border_size.y)
		box.pos = vec2(-border_size.x / 2, 0)
		self.objects.append(box)
		box = ObjectAbstract()
		box.color = '#8b5c29'
		box.shape = Shape.BOX
		box.size = vec2(border_size.x, 4)
		box.pos = vec2(0, border_size.y / 2)
		self.objects.append(box)
		box = ObjectAbstract()
		box.color = '#8b5c29'
		box.shape = Shape.BOX
		box.size = vec2(border_size.x, 4)
		box.pos = vec2(0, -border_size.y / 2)
		self.objects.append(box)
		
		for p in self.players:
			p.my_paddle = ObjectPaddle(p.name)
			p.my_paddle.size = vec2(16, 16)
			p.my_paddle.pos = vec2(0, 0)
			p.my_paddle.controler = p.name
			self.objects.append(p.my_paddle)
		pass


	def	update_world_state(self):
		if (self.game_state == GameState.LOBBY and self.next_state == GameState.SETTING_UP):
			self.create_game_world()

		self.game_state = self.next_state
		if (self.game_state == GameState.LOBBY):
			self.next_state = GameState.SETTING_UP
			self.create_game_lobby()
		elif (self.game_state == GameState.SETTING_UP and len(self.players) < 2):
			self.next_state = GameState.LOBBY
			self.state_timer = time.time() + 999999.0
			self.game_event_message("Not enough players", 4.0, 'error')
			self.game_event_message("Stopping timer", 4.0, 'error')
		elif (self.game_state == GameState.SETTING_UP):
			self.state_timer = time.time() + self.TIME_GAME_RUN
			self.in_game_ball.pos = vec2(0, 0)
			self.in_game_ball.speed = 0.0
			random_rot = (0.0, math.pi)[randint(0, 1)] + uniform(-1.1, 1.1) # Random direction
			self.in_game_ball.init_rotation(random_rot)
			self.next_state = GameState.IN_GAME
		elif (self.game_state == GameState.IN_GAME):
			# If the game score is not reached --> loop state
			if (self.in_game_players[0].score >= self.SCORE_MAX or self.in_game_players[1].score >= self.SCORE_MAX):
				player = self.in_game_players[0] if self.in_game_players[0].score >= self.SCORE_MAX else self.in_game_players[1]
				list_of_non_players = [p for p in self.players if next((p2 for p2 in self.in_game_players if p2.id == p.id), None) == None]
				self.game_event_message(f"'{player.name.upper()}'  WON !", 6.0, 'boom', list_of_non_players)
				self.game_event_message(f"YOU  WON !!!", 6.0, 'boom', [player])
				self.game_event_message(f"Your opponent won...", 6.0, 'error', [p for p in self.in_game_players if p.id != player.id])
				self.reset_game()
				self.update_world_state()
			else:
				self.state_timer = time.time() + 999999.0
				self.in_game_ball.speed = 16.0
				self.next_state = GameState.SETTING_UP

	def player_scored(self, player: Player):
		player.score += 1
		list_of_non_players = [p for p in self.players if next((p2 for p2 in self.in_game_players if p2.id == p.id), None) == None]
		self.game_event_message(f"'{player.name}' scored !", 3.0, 'boom', list_of_non_players)
		self.game_event_message(f"You scored !", 3.0, 'boom', [player])
		self.game_event_message(f"Your opponent scored !", 3.0, 'error', [p for p in self.in_game_players if p.id != player.id])
		self.game_event_message(f"score: {player.score}", 3.0,)
		pass

	def	_game_start(self) -> bool:
		self.update_world_state()
		return True

	def	_game_stop(self) -> bool:
		self.reset_game()
		return True

	def	_game_loop(self) -> bool:

		# Check if game is in lobby
		if (self.game_state == GameState.LOBBY):
			if (len(self.players) >= 2 and self.state_timer > time.time() + 9999.0):
				self.game_event_message(f"Game starting in {round(self.TIME_GAME_START, 1)}S...", 4.0)
				self.state_timer = time.time() + self.TIME_GAME_START

		# Check for state change
		if (time.time() > self.state_timer):
			self.update_world_state()

		diff_time = round(self.state_timer - time.time() + 0.5)
		if (diff_time <= 3 and diff_time != self.old_time):
			self.game_event_message(f"{diff_time}...", 0.8)
			self.old_time = diff_time

		if (self.game_state == GameState.IN_GAME):
			if (self.in_game_ball.pos.y > self.TERRAIN_SIZE.y / 2):
				self.player_scored(self.in_game_players[1])
				self.state_timer = 0.0
			elif (self.in_game_ball.pos.y < -self.TERRAIN_SIZE.y / 2):
				self.player_scored(self.in_game_players[0])
				self.state_timer = 0.0

		return True
	
	def	_game_join(self, player: Player) -> bool:
		self.game_event_message(f"'{player.name}' joined the party", 2.0)

		# GAME IS IN LOBBY
		if (self.game_state == GameState.LOBBY):
			if (not (player.name in self.already_joined)):
				self.already_joined.append(player.name)
				player.my_paddle = ObjectPaddle(player.name)
				player.my_paddle.size = vec2(16, 16)
				player.my_paddle.pos = vec2(0, 0)
				player.my_paddle.controler = player.name
				self.objects.append(player.my_paddle)

		return True

	def	_game_leave(self, player: Player) -> bool:

		if (self.game_state == GameState.LOBBY):
			if (len(self.players) == 2):
				self.state_timer = time.time() + 999999.0
				self.game_event_message("Not enough players", 4.0, 'error')
				self.game_event_message("Stopping timer", 4.0, 'error')

		self.game_event_message(f"Player '{player.name}' left the party", 2.0)

		return True

	# Game send update
	def _game_send_update(self):
		return True
