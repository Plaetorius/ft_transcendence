##########
# IMPORT #
##########

from ..classes.party import ( Party )
from ..classes.player import ( Player )
from ..classes.objects import ( Shape, Collision, ObjectAbstract)
from ..classes.math_vec2 import ( vec2 )
from random import randint, uniform

import random, math, time


#####################
# GLOBALS VARIABLES #
#####################

TERRAIN_SIZE: vec2	= vec2(300, 600)
space_terrain		= 50


##################
# CLASS FAKEBALL #
##################

class FakeBall(ObjectAbstract):
	def __init__(self, match, t_party):
		super().__init__()
		self.shape		= Shape.BALL
		self.color		= '#0066b1'
		self.size		= vec2(15, 20)
		self.speed		= 10
		self.accel		= 0.12
		self.vel		= vec2(0, 0)
		self.match		= match
		self.t_party	= t_party
		self.collide	= Collision.BOUNCE

		self.fake_init()

	def fake_init(self):
		self.bouge		= 0
		self.rot 		= (0, math.pi)[randint(0, 1)]  + uniform(-math.pi / 4, math.pi / 4)
		self.pos 		= self.match.center
		self.dir 		= vec2(math.sin(self.rot), math.cos(self.rot))
		self.vel 		= vec2(0, 0)
		self.speed 		= 10
		self.old_dir 	= self.dir

	def update(self):
		if self.match.end == True:
			return
		if (self.pos.y > TERRAIN_SIZE.y / 2):
			self.t_party.player_scored(self.match.player2, self.match)
			self.fake_init()
		if (self.pos.y < -TERRAIN_SIZE.y / 2):
			self.t_party.player_scored(self.match.player1, self.match)
			self.fake_init()
		
		if ((self.old_dir.y < 0 and self.dir.y >= 0) or (self.old_dir.y >= 0 and self.dir.y < 0)):
			self.speed = self.speed * (1.0 + self.accel)

		if self.bouge >= 50:
			self.speed = 16
			self.pos = self.pos + self.vel
		else :
			self.bouge += 1
			self.speed = 0

		self.vel	= self.dir * self.speed
		self.old_dir = self.dir

		pass


####################
# CLASS FAKEPADDLE #
####################

class FakePaddle(ObjectAbstract):
	def __init__(self, controler: str, control_left: str, control_right: str):
		super().__init__()
		self.shape		= Shape.PADDLE
		self.left		= control_left
		self.right		= control_right
		self.size		= vec2(64, 12)
		self.collide	= Collision.STOP
		self.controler	= controler
		random.seed(controler + str(time.time()))
		r = lambda: random.randint(75, 175)
		self.color		= '#{:02x}{:02x}{:02x}'.format(r(), r(), r())

		pass

	def control(self, key_values):
		val_sin = math.sin(self.rot)
		val_cos = math.cos(self.rot)
		direction = vec2(0, 0)
		if (key_values.get(self.left, False)):
			direction.x += +val_cos
			direction.y += -val_sin
		
		if (key_values.get(self.right, False)):
			direction.x += -val_cos
			direction.y += +val_sin

		self.vel = direction * 10
  
		pass

	def update(self):
		self.pos = self.pos + self.vel
		pass


####################
# CLASS FAKEPLAYER #
####################

class FakePlayer():
	def __init__(self, name, left_control, right_control):
		self.name = name
		self.score = 0
		self.in_game = False
		self.is_winner = False
		self.paddle: FakePaddle = None
		self.control_left = left_control
		self.control_right = right_control
	
	def __repr__(self) -> str:
		return "name: " + self.name
	
	def to_dict(self):
		return {
			"name": self.name,
		}


###################
# CLASS FAKEMATCH #
###################

class FakeMatch():
	def __init__(self, player1: FakePlayer, player2: FakePlayer, t_party, ide = 0):
		self.player1 = player1
		self.player2 = player2
		self.party = t_party
		self.ide = ide
		self.center: vec2 = vec2(self.ide * TERRAIN_SIZE.x + (self.ide * space_terrain) , 0)
		self.objects = []
		self.end = False
		self.timer = time.time()


	def create_objects(self):
		terrain = ObjectAbstract()
		terrain.shape = Shape.TERRAIN
		terrain.size = TERRAIN_SIZE
		terrain.color = '#ffe1ba'
		terrain.pos = vec2(self.center.x, 0)
		self.objects.append(terrain)
		mur1 				= ObjectAbstract()
		mur1.color			= '#8b5c29'
		mur1.size.y 		= TERRAIN_SIZE.y
		mur1.pos 			= vec2(self.center.x - TERRAIN_SIZE.x / 2, 0)
		self.objects.append(mur1)
		mur2 				= ObjectAbstract()
		mur2.color			= '#8b5c29'
		mur2.size.y 		= TERRAIN_SIZE.y
		mur2.pos 			= vec2(self.center.x + TERRAIN_SIZE.x / 2, 0)
		self.objects.append(mur2)
		ball 				= FakeBall(self, self.party)
		ball.pos 			= vec2(self.center.x, 0)
		self.objects.append(ball)
		self.party.objects.extend(self.objects)


	def teleport_all_paddles(self):
		self.player1.paddle.pos.x = self.center.x
		self.player1.paddle.pos.y = TERRAIN_SIZE.y / 2
		self.player1.paddle.rot = math.pi
		self.player2.paddle.pos.x = self.center.x
		self.player2.paddle.pos.y = -TERRAIN_SIZE.y / 2
		self.player2.paddle.rot = 0


	def start_match(self):
		self.player1.in_game = True
		self.player2.in_game = True
		self.party.create_player_paddle([self.player1, self.player2])
		self.player1.score = 0
		self.player2.score = 0
		self.teleport_all_paddles()
		self.create_objects()


	def end_match(self):
		self.player1.in_game = False
		self.player2.in_game = False
		self.player1.score = 0
		self.player2.score = 0
		self.party.obj_to_remove.extend([self.player1.paddle, self.player2.paddle])
		self.party.obj_to_remove.extend(self.objects)
		self.objects = []
		self.end = True
	
	def all_match_end(self, matchs):
		for match in matchs:
			if match.end == False:
				return False
		return True


#############################
# CLASS PONGTOURNAMENTLOCAL #
#############################

class PongTournamentLocal(Party):
	def __init__(self, multi = False):
		super().__init__()
		self.name								= "Local Pong"
		self.max_players						= 1
		self.playersF: list[FakePlayer]			= []
		self.matchs: list[FakeMatch]			= []
		self.end: bool							= False
		self.multi								= multi
		self.namer								= ""


	def create_player_paddle(self, players):
		for player in players:
			player.paddle = FakePaddle(self.namer, player.control_left, player.control_right)
			self.objects.append(player.paddle)


	def create_player(self):
		player1 = FakePlayer(self.namer + "_1", "a", "d")
		player2 = FakePlayer(self.namer + "_2", "j", "l")
		if self.multi == True:
			player3 = FakePlayer(self.namer + "_3", "arrowleft", "arrowright")
			player4 = FakePlayer( self.namer + "_4", "4", "6")
			self.playersF.extend([player1, player2, player3, player4])
			self.__create_match(player1, player2, 0.5)
			self.__create_match(player3, player4, -0.5)
		else :
			self.playersF.extend([player1, player2])
			self.__create_match(player1, player2, 0)

	def reset_game(self):
		self.matchs = []
		self.playersF = []
		self.end = False
		self.obj_to_remove.extend(self.objects)

	
	def __create_match(self, player1: FakePlayer, player2: FakePlayer, ide = 0):
		match = FakeMatch(player1, player2, self, ide)
		self.matchs.append(match)
		match.start_match()

	def player_scored(self, player: FakePlayer, match: FakeMatch):
		player.score += 1
		self.game_event_message(f"player '{player.name}' Scored : {match.player1.score} / {match.player2.score}", 2.0, 'boom')
		if player.score >= 5:
			player.is_winner = True
			self.game_event_message(f"winner = '{player.name}'", 2.0, 'success')
			match.end_match()
			if match.all_match_end(self.matchs) == True:
				winners = [player for player in self.playersF if player.is_winner == True]
				print(winners)
				if len(self.matchs) == 1:
					self.end = True
				else:
					self.matchs = []
					winners[0].is_winner = False
					winners[1].is_winner = False
					self.__create_match(winners[0], winners[1], 0)


	def	_game_start(self) -> bool:
		return True

	def	_game_stop(self) -> bool:
		return True

	# loop for the game
	def	_game_loop(self) -> bool:
		if self.end == True:
			self.reset_game()
			self.create_player()
			self.game_event_message("New game started", 2.0, 'success')
		return True

	def	_game_join(self, player: Player) -> bool:
		self.namer = player.name			#todo add camera.pos(0 500 0)
		self.create_player()
		self.game_event_message("Game started", 2.0, 'success')
		return True

	# destroy player from list player
	def	_game_leave(self, player: Player) -> bool:
		self.reset_game()
		return True

	def _game_send_update(self):
 		return True
		

