##########
# IMPORT #
##########

from ..classes.party import ( Party )
from ..classes.player import ( Player )
from ..classes.objects import ( Shape, ObjectAbstract, ObjectBall, ObjectTerrain, ObjectPaddle, Collision)

from ..classes.math_vec2 import ( vec2 )
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from users.elo import ( game_result )
from channels.layers import get_channel_layer
from datetime import timedelta
from users.models import MatchHistory, PlayerMatchHistory
from django.contrib.auth import get_user_model
User = get_user_model()

import uuid
import time
import random
from random import randint, uniform
import math


#####################
# GLOBALS VARIABLES #
#####################

TERRAIN_SIZE: vec2	= vec2(300, 600)
space_terrain	= 50


####################
# GLOBAL FUNCTIONS #
####################

# check if the number is a power of two
def __ispoweroftwo__(n: int) -> bool:
	test = n & (n-1) == 0 and n != 0 and n != 1
	return test

# get user from database
@database_sync_to_async
def get_user(field: str) -> User:
	return User.objects.get(username=field)

# send history to database
def send_history( name1: str, name2: str, winner: str, score, game_time, game_type: str):
	user1 = async_to_sync(get_user)(name1)
	user2 = async_to_sync(get_user)(name2)
	elo = [user1.elo, user2.elo]
	actual_time = time.time() - game_time
	duration_timedelta = timedelta(seconds=actual_time)
	if winner == name1:
		elo_list = game_result(user1, user2, 1)
	else:
		elo_list = game_result(user2, user1, 1)
	elo = [elo[i] - elo_list[i] for i in range(2)]
	# Winner elo and score are always in first place
	elo.sort(reverse=True)
	score.sort(reverse=True)
	match = MatchHistory.objects.create(game_type=game_type, duration=duration_timedelta)
	pmh1 = PlayerMatchHistory.objects.create(player=user1, match=match, score=score[0], elo_change=elo[0])
	pmh2 = PlayerMatchHistory.objects.create(player=user2, match=match, score=score[1], elo_change=elo[1])
	match.save()
	pmh1.save()
	pmh2.save()


##########################
# CLASS TOURNAMENTPADDLE #
##########################

class TournamentPaddle(ObjectAbstract):
	def __init__(self, controler: str):
		super().__init__()
		self.shape		= Shape.PADDLE
		
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
	


########################
# CLASS TOURNAMENTBALL #
########################

class TournamentBall(ObjectAbstract):
	def __init__(self, match, t_party):
		super().__init__()
		self.shape		= Shape.BALL
		self.size		= vec2(20, 20)
		self.speed		= 16
		self.accel		= 0.02
		self.vel		= vec2(0, 0)
		self.match		= match
		self.t_party	= t_party
		self.collide	= Collision.BOUNCE

		self.fake_init()

	def fake_init(self):
		self.bouge		= 0
		self.rot 		= (0, math.pi)[randint(0, 1)]  + uniform(-math.pi / 4, math.pi / 4)
		self.pos 		= self.match.terrain.pos
		self.dir 		= vec2(math.sin(self.rot), math.cos(self.rot))
		self.vel 		= vec2(0, 0)
		self.first		= 0
		self.speed 		= 0
		self.old_dir 	= self.dir

	def update(self):
		if self.match.winner != None:
			return

		if (self.pos.y > TERRAIN_SIZE.y / 2):
			self.t_party.player_scored(self.match.players[1])
			self.fake_init()
		if (self.pos.y < -TERRAIN_SIZE.y / 2):
			self.t_party.player_scored(self.match.players[0])
			self.fake_init()
		
		if ((self.old_dir.y < 0 and self.dir.y >= 0) or (self.old_dir.y >= 0 and self.dir.y < 0)):
			self.speed = self.speed * (1.0 + self.accel)

		if self.bouge >= 50:
			if self.first == 0:
				self.speed = 16
				self.first = 1
			self.pos = self.pos + self.vel
		else :
			self.bouge += 1
			self.speed = 0

		self.vel	= self.dir * self.speed
		self.old_dir = self.dir

		pass


##########################
# CLASS PLAYERTOURNAMENT #
##########################

class PlayerTournament(Player):
	def __init__(self, player):
		super().__init__(player.name, player.id)
		self.player			= player
		self.score			= 0
		self.matchs: Match 	= None
		self.paddle			= None
		self.in_game		= False
		self.loose 			= False

	def __repr__(self):
		return "player" + str(self.player.to_dict()) + "score" + str(self.score)


###############
# CLASS MATCH #
###############

class Match:
	def __init__(self, players: list[PlayerTournament]):
		self.players: list[PlayerTournament] = players
		self.score							 = [0, 0]
		self.winner							 = None
		self.objects						 = []
		self.ball:TournamentBall			 = None
		self.terrain : TournamentTerrain	 = None
		self.time 							 = time.time()
		
	# create terrain and ball
	def __create_terrain__(self, j: int, t_party):
		self.objects			= []
		self.terrain 			= ObjectTerrain()
		self.terrain.size 		= TERRAIN_SIZE
		self.terrain.pos.x 		= j * TERRAIN_SIZE.x + (j * space_terrain)
		self.terrain.pos.y 		= 0
		self.objects.append(self.terrain)
		mur1 				= ObjectAbstract()
		mur1.size.y 		= TERRAIN_SIZE.y
		mur1.pos 			= vec2(self.terrain.pos.x - TERRAIN_SIZE.x / 2, 0)
		self.objects.append(mur1)
		mur2 				= ObjectAbstract()
		mur2.size.y 		= TERRAIN_SIZE.y
		mur2.pos 			= vec2(self.terrain.pos.x + TERRAIN_SIZE.x / 2, 0)
		self.objects.append(mur2)
		self.ball 				= TournamentBall(self, t_party)
		self.ball.pos 			= vec2((j * TERRAIN_SIZE.x) + (j * space_terrain), 0)
		self.objects.append(self.ball)
		t_party.objects.extend(self.objects)

	def to_dict(self):
		return {
			"players": [player.to_dict() for player in self.players],
			"score": self.score,
			"winner": self.winner.to_dict() if self.winner else None
	}

	def __str__(self):
		return f"Match between {self.players[0].name} and {self.players[1].name}"


########################
# CLASS PONGTOURNAMENT #
########################

class pongTournament(Party):
	def __init__(self):
		super().__init__()
		self.name								= "Pong Tournament"
		self.timerupdate						= 12
		self.max_players						= 32
		self.timer								= self.timerupdate
		self.activateTimer						= False
		self.gameStarted						= False
		self.playersT: list [PlayerTournament]	= []
		self.autPlayer:	list [PlayerTournament]	= []
		self.matchs: list[Match]				= []
		self.end: bool							= False


	# teleport player for game
	def teleport_players(self):
		for j, matchs in enumerate(self.matchs):
			for i, player in enumerate(matchs.players):
				if i & 1 == 0:
					player.paddle.pos.x = j * TERRAIN_SIZE.x + (j * space_terrain)
					player.paddle.pos.y = TERRAIN_SIZE.y / 2
					player.paddle.rot = math.pi
				else:
					player.paddle.pos.x = j * TERRAIN_SIZE.x + (j * space_terrain)
					player.paddle.pos.y = -TERRAIN_SIZE.y / 2
					player.paddle.rot = 0


	# reset all player paddle before create new match
	def remove_all_object(self):
		self.obj_to_remove.extend(self.objects)

	# reset all paddle
	def reset_paddles(self):
		for player in self.playersT:
			if player.paddle != None:
				self.obj_to_remove.append(player.paddle)
		for test in self.playersT:
			test.paddle = TournamentPaddle(test.name)
			test.paddle.pos = vec2(-2000, -2000)
			self.objects.append(test.paddle)


	# create matchs and terrain
	def reset_game(self):
		self.gameStarted	= False
		self.activateTimer	= False
		self.timer 			= self.timerupdate
		self.autPlayer 		= []
		self.end: bool		= False
		self.remove_all_object()

		self.game_event_global_message("A new tournament started !", 3.0)

	# create all matches
	def __create_Matches__(self):
		self.matchs: list [Match] = []
		for i in range(0, len(self.playersT), 1):
			temp_player1 = next((player for player in self.playersT if player.in_game == False and player.loose == False), None)
			if temp_player1 != None:
				temp_player1.in_game = True
				temp_player2 = next((player for player in self.playersT if player.in_game == False and player.loose == False), None)
				if temp_player2 != None:
					temp_player2.in_game = True
					self.matchs.append(Match([temp_player1, temp_player2]))
					temp_player1.matchs = self.matchs[i]
					temp_player2.matchs = self.matchs[i]
					self.matchs[i].__create_terrain__(i, self)
				else:
					if i == 0:
						# destroy and kick last player
						self.end = True
						temp_player1.in_game = False
						self.game_event_message("You Win the tournament !", 4.0, 'boom', [temp_player1])
						self.autPlayer.remove(temp_player1)
						self.game_event_disconnect(temp_player1)
		if self.end == False:
			self.autPlayer = self.playersT.copy()
		self.reset_paddles()
		self.teleport_players()

	# check if all matchs are ended
	def all_match_end(self) -> bool:
		for match in self.matchs:
			if match.winner == None:
				return False
		self.obj_to_remove.extend(self.objects)
		for player in self.playersT:
			player.paddle = None
		self.__create_Matches__()
		return True


	# check if player scored
	def player_scored(self, player: PlayerTournament):
		player.score += 1
		player.matchs.score[0] = player.matchs.players[0].score
		player.matchs.score[1] = player.matchs.players[1].score
		self.game_event_message(f"score : {player.matchs.score[0]} | {player.matchs.score[1]}", 3.0, '', player.matchs.players)
		if player.score >= 5 and player.matchs.winner == None:
			player.matchs.winner = player.name
			for joueur in player.matchs.players:
				if joueur != player and joueur != None: 
					player.in_game = False
					joueur.in_game = False
					joueur.loose = True
					send_history(player.name, joueur.name, player.name, [player.score, joueur.score], player.matchs.time, "Ranked")
					self.game_event_message("You loose the match ! looooser....", 4.0, 'error', [joueur])
					player.matchs.players.remove(joueur)
					self.autPlayer.remove(joueur)
					self.obj_to_remove.append(joueur.paddle)
					self.game_event_disconnect(joueur)
					player.score = 0
					player.matchs.winner = player.name
					self.all_match_end()
		else:
			self.game_event_message(f"player: '{player.name}' scored", 3, 'boom', player.matchs.players)

	# method for class party
	def	_game_start(self) -> bool:
		return True

	def	_game_stop(self) -> bool:
		return True

	# loop for the game
	def	_game_loop(self) -> bool:
		actual_time = time.time()
		# check if the players is ready to start the game (power of two)
		if self.gameStarted == False and self.activateTimer == True:
			if actual_time > self.timer:
				if __ispoweroftwo__(len(self.playersT)) == True:
					self.gameStarted = True
					self.activateTimer = False
				else:
					self.timer += self.timerupdate
					self.game_event_message("Player not pow of two", 3.0, 'error')
					self.game_event_message("Game start in 10 second", 3.0, 'error')
		# check if the game is started
		if self.gameStarted == True:
			if len(self.matchs) == 0:
				self.remove_all_object()
				self.game_event_message("TOURNAMENT BEGIN !", 3.0, 'success')
				self.__create_Matches__()
				if self.end == False:
					self.autPlayer = self.playersT.copy()
			return True

	def	_game_join(self, player: Player) -> bool:
		if self.activateTimer == False:
			self.activateTimer = True
			self.timer = time.time() + self.timerupdate

		# check if the player is already in the game
		temp_player = next((test for test in self.autPlayer if player.id == test.id), None)
		
		# check if the game is started for stop player to join
		if self.gameStarted == True:
			if temp_player == None:
				return False

		# check if the player is already in the game for create new player
		if len(self.playersT) < self.max_players:
			if temp_player == None:
				temp_player = PlayerTournament(player)
				temp_player.paddle = TournamentPaddle(temp_player.name)
				self.objects.append(temp_player.paddle)
				self.autPlayer.append(temp_player)
			self.playersT.append(temp_player)
			self.game_event_message(f"Player '{temp_player.name}' joined the tournament", 1.0)
			return True
		return False

	# destroy player from list player
	def	_game_leave(self, player: Player) -> bool:
		playerdelet = next((test for test in self.playersT if player.id == test.id), None)
		if playerdelet != None:
			self.game_event_message(f"Player '{playerdelet.name}' leave the tournament", 1.0)
			self.playersT.remove(playerdelet)
		if (len(self.playersT) == 0):
			self.reset_game()
			
		return True

	def _game_send_update(self):
 		return True