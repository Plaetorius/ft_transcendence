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

size_terrain	= 250
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


########################
# CLASS TOURNAMENTTEXT #
########################

# class TournamentText(ObjectAbstract):
# 	def __init__(self, text: str):
# 		super().__init__()
# 		self.shape		= Shape.TEXT
# 		self.color		= '#EEEEEE'
# 		self.size		= vec2(25, 30)
# 		self.controler	= None
# 		self.collide	= Collision.NONE
# 		self.text		= text
	
# 	def to_dict(self):
# 		return {
# 			"uuid": self.uuid,
# 			"controler": self.controler,
# 			"shape": str(self.shape),
# 			"pos": self.pos.to_dict(),
# 			"vel": self.vel.to_dict(),
# 			"size": self.size.to_dict(),
# 			"rot": self.rot,
# 			"color": self.color,
# 			"text": self.text,
# 		}
	


##########################
# CLASS TOURNAMENTPADDLE #
##########################

class TournamentPaddle(ObjectAbstract):
	def __init__(self, controler: str):
		super().__init__()
		self.shape		= Shape.PADDLE
		
		self.size		= vec2(120, 20)
		self.collide	= Collision.STOP
		self.controler	= controler
		self.user		= get_user(controler)
		#if self.user.color_paddle == None:
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

		self.vel = direction * 12
  
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
		self.bouge		= 0
		self.shape		= Shape.BALL
		self.size		= vec2(20, 20)
		self.rot		= (0, math.pi)[randint(0, 1)] + uniform(-math.pi / 4, math.pi / 4)
		self.speed		= 16
		self.dir		= vec2(math.sin(self.rot), math.cos(self.rot))
		self.vel		= vec2(0, 0)
		self.match		= match
		self.t_party	= t_party
		self.collide	= Collision.BOUNCE

	def fake_init(self):
		self.bouge		= 0
		self.rot 		= (0, math.pi)[randint(0, 1)]  + uniform(-math.pi / 4, math.pi / 4)
		self.pos 		= self.match.terrain.pos
		self.dir 		= vec2(math.sin(self.rot), math.cos(self.rot))
		self.vel 		= vec2(0, 0)

	def update(self):
		if self.match.winner != None:
			return


		if (self.pos.y > (size_terrain * 4) / 2):
			self.t_party.player_scored(self.match.players[1])
			self.fake_init()
		if (self.pos.y < -(size_terrain * 4) / 2):
			self.t_party.player_scored(self.match.players[0])
			self.fake_init()

		if self.bouge >= 50:
			self.speed = 16
			self.pos	= self.pos + self.vel
		else :
			self.bouge += 1
			self.speed = 0
		self.vel	= self.dir * self.speed

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
		# self.text_game: TournamentText	= False

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
		# self.texte: TournamentText			 = None
		self.terrain : TournamentTerrain	 = None
		
	# create terrain and ball
	def __create_terrain__(self, j: int, t_party):
		self.objects			= []
		self.terrain 			= ObjectTerrain()
		self.terrain.size 		= vec2(3, 4) * size_terrain
		self.terrain.pos.x 		= j * 3 * size_terrain + (j * space_terrain)
		self.terrain.pos.y 		= 0
		self.objects.append(self.terrain)
		# self.texte 				= TournamentText(f"{str(self.score)}")
		# self.texte.pos			= vec2((j * 3 * size_terrain) + (j * space_terrain), 0)
		# self.texte.size.y		= 500
		# self.objects.append(self.texte)
		mur1 				= ObjectAbstract()
		mur1.size.y 		= size_terrain * 4
		mur1.pos 			= vec2(self.terrain.pos.x - size_terrain * 3 / 2, 0)
		self.objects.append(mur1)
		mur2 				= ObjectAbstract()
		mur2.size.y 		= size_terrain * 4
		mur2.pos 			= vec2(self.terrain.pos.x + size_terrain * 3 / 2, 0)
		self.objects.append(mur2)
		self.ball 				= TournamentBall(self, t_party)
		self.ball.pos 			= vec2((j * 3 * size_terrain) + (j * space_terrain), 0)
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
					player.paddle.pos.x = j * 3 * size_terrain + (j * space_terrain)
					player.paddle.pos.y = size_terrain * 2
					player.paddle.rot = math.pi
				else:
					player.paddle.pos.x = j * 3 * size_terrain + (j * space_terrain)
					player.paddle.pos.y = -size_terrain * 2
					player.paddle.rot = 0


	# reset all player paddle before create new match
	def remove_all_object(self):
		# self.obj_to_remove.extend([obj for obj in self.objects if obj.shape == Shape.PADDLE])
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

		self.game_event_global_message("A new tournament started !", 2.0)

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
					# temp_player1.text_game = TournamentText(temp_player1.score)
					# temp_player2.text_game = TournamentText(temp_player2.score)
					self.matchs.append(Match([temp_player1, temp_player2]))
					temp_player1.matchs = self.matchs[i]
					temp_player2.matchs = self.matchs[i]
					self.matchs[i].__create_terrain__(i, self)
				else:
					if i == 0:
						# destroy and kick last player
						self.end = True
						temp_player1.in_game = False
						self.game_event_message("You Win the tournament !", 2.0, [temp_player1])
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


	# todo send history of match to database

	# check if player scored
	def player_scored(self, player: PlayerTournament):
		player.score += 1
		player.matchs.score[0] = player.matchs.players[0].score
		player.matchs.score[1] = player.matchs.players[1].score
		# player.matchs.texte.text = (f"{player.matchs.score[0]} | {player.matchs.score[1]}")
		self.game_event_message(f"score : {player.matchs.score[0]} | {player.matchs.score[1]}", 1, player.matchs.players)
		if player.score >= 5 and player.matchs.winner == None:
			player.matchs.winner = player.name
			for joueur in player.matchs.players:
				if joueur != player and joueur != None: 
					player.in_game = False
					joueur.in_game = False
					joueur.loose = True
					self.game_event_message("You loose the match ! looooser....", 2.0, [joueur])
					#! ADD MATCH HISTORY HERE AND ELO 
					#self.send_history(player.matchs)
					player.matchs.players.remove(joueur)
					self.autPlayer.remove(joueur)
					self.obj_to_remove.append(joueur.paddle)
					self.game_event_disconnect(joueur)
					player.score = 0
					player.matchs.winner = player.name
					self.all_match_end()
		else:
			self.game_event_message(f"player: '{player.name}' scored", 1, player.matchs.players)

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
			# texte = next((obj for obj in self.objects if obj.shape == Shape.TEXT), None)
			# if texte != None:
			# 	texte.text = f"game start in {round(self.timer - actual_time, 0)} seconds"
			if actual_time > self.timer:
				if __ispoweroftwo__(len(self.playersT)) == True:
					self.gameStarted = True
					self.activateTimer = False
				else:
					self.timer += self.timerupdate
					self.game_event_message("You need to be a power of two to start the game", 1.0)
					self.game_event_message("game start in 10 second", 1.0)
		# check if the game is started
		if self.gameStarted == True:
			if len(self.matchs) == 0:
				self.remove_all_object()
				self.game_event_message("TOURNAMENT BEGIN !", 1.0)
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
			self.game_event_message(f"game start every 10s", 1.0, [temp_player])
			self.game_event_message(f"player '{temp_player.name}' joined the tournament", 1.0)
			return True
		return False

	# destroy player from list player
	def	_game_leave(self, player: Player) -> bool:
		playerdelet = next((test for test in self.playersT if player.id == test.id), None)
		if playerdelet != None:
			self.game_event_message(f"player '{playerdelet.name}' leave the tournament", 1.0)
			self.playersT.remove(playerdelet)
		if (len(self.playersT) == 0):
			self.reset_game()
			
		return True

	def _game_send_update(self):
 		return True
