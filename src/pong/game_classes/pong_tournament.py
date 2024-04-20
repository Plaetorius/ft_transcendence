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
from django.contrib.auth import get_user_model
User = get_user_model()

import uuid
import time
from random import randint, uniform
import math


#####################
# GLOBALS VARIABLES #
#####################

size_terrain	= 250
space_terrain	= 50


########################
# CLASS TOURNAMENTBALL #
########################

class TournamentBall(ObjectAbstract):
	def __init__(self, match, t_party):
		super().__init__()
		self.shape		= Shape.BALL
		self.size		= vec2(20, 20)
		self.rot		= (0, math.pi)[randint(0, 1)] + uniform(-math.pi / 4, math.pi / 4)
		self.speed		= 16
		self.dir		= vec2(math.sin(self.rot), math.cos(self.rot))
		self.vel		= self.dir * self.speed
		self.match		= match
		self.t_party	= t_party
		self.collide	= Collision.BOUNCE

	def fake_init(self):
		self.rot 		= (0, math.pi)[randint(0, 1)]  + uniform(-math.pi / 4, math.pi / 4)
		self.pos 		= self.match.objects[0].pos
		self.dir 		= vec2(math.sin(self.rot), math.cos(self.rot))
		self.vel 		= self.dir * self.speed

	def update(self):
		if self.match.winner != None:
			return
		if (self.pos.y > (size_terrain * 4) / 2):
			self.t_party.player_scored(self.match.players[1])
			self.fake_init()
		if (self.pos.y < -(size_terrain * 4) / 2):
			self.t_party.player_scored(self.match.players[0])
			self.fake_init()
		
		self.pos		= self.pos + self.vel
		self.vel		= self.dir * self.speed
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
		self.players: list[PlayerTournament] = players.copy()
		self.score: list[int]				 = 0
		self.winner							 = None
		self.objects						 = []
		
	# create terrain and ball
	def __create_terrain__(self, j: int, t_party):
		self.objects		= []
		terrain 			= ObjectTerrain()
		terrain.size 		= vec2(3, 4) * size_terrain
		terrain.pos.x 		= j * 3 * size_terrain + (j * space_terrain)
		terrain.pos.y 		= 0
		self.objects.append(terrain)
		mur1 				= ObjectAbstract()
		mur1.size.y 		= size_terrain * 4
		mur1.pos 			= vec2(terrain.pos.x - size_terrain * 3 / 2, 0)
		self.objects.append(mur1)
		mur2 				= ObjectAbstract()
		mur2.size.y 		= size_terrain * 4
		mur2.pos 			= vec2(terrain.pos.x + size_terrain * 3 / 2, 0)
		self.objects.append(mur2)
		ball 				= TournamentBall(self, t_party)
		ball.pos 			= vec2((j * 3 * size_terrain) + (j * space_terrain), 0)
		self.objects.append(ball)
		t_party.objects.extend(self.objects)

	def to_dict(self):
		return {
			"players": [player.to_dict() for player in self.players],
			"score": self.score,
			"winner": self.winner.to_dict() if self.winner else None
	}

	def __str__(self):
		return f"Match between {self.players[0].name} and {self.players[1].name}"


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
# CLASS PONGTOURNAMENT #
########################

class pongTournament(Party):
	def __init__(self):
		super().__init__()
		self.name								= "Pong Tournament"
		self.timerupdate						= 12
		self.max_players						= 64
		self.timer								= self.timerupdate
		self.activateTimer						= False
		self.gameStarted						= False
		self.playersT: list [PlayerTournament]	= []
		self.autPlayer:	list [PlayerTournament]	= []
		self.matchs: list[Match]				= []
		self.tick								= 0
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
	def reset_autPlayer_paddle(self):
		for player in self.autPlayer:
			if player.paddle != None:
				self.obj_to_remove.append(player.paddle)


	# reset all paddle
	def reset_paddles(self):
		for player in self.playersT:
			if player.paddle != None:
				self.obj_to_remove.append(player.paddle)
		for test in self.playersT:
			test.paddle = ObjectPaddle(test.name)
			test.paddle.pos = vec2(-1000, -1000)
			test.paddle.size = vec2(120, 20)
			self.objects.append(test.paddle)


	# create matchs and terrain
	def reset_game(self):
		self.gameStarted	= False
		self.activateTimer	= False
		self.timer 			= self.timerupdate
		self.autPlayer 		= []
		self.tick			= 0
		self.end: bool		= False


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
						self.autPlayer.remove(temp_player1)
						# reset game
						self.reset_game()
						try:
							async_to_sync (self.channel_layer.group_send)(self.party_channel_name, {"type": "leave_party", "user_id": temp_player1.id}) # kick loser
						except Exception as e:
							print(f"#### __create_Matches__ Party: ERROR: {e}")
						# reset all player for reset game
						self.playersT = []
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


	# send history of match to database
	def send_history(self, match: Match):
		user1 = async_to_sync(get_user)(match.players[0].name)
		user2 = async_to_sync(get_user)(match.players[1].name)
		winner = match.winner
		looser = next((player for player in match.players if player.name != winner), None)
		if winner == user1:
			elo_list = game_result(user1, user2, 1)
			# or elo_list = game_result(winner, looser, 1) but we need user1 and user2 for database i think ?
		else:
			elo_list = game_result(user2, user1, 1)
		score  = match.score
		#todo add database, TOM FAIT LE STP


	# check if player scored
	def player_scored(self, player: PlayerTournament):
		#todo create front for score and timer
		player.score += 1
		if player.score >= 5 and player.matchs.winner == None:
			player.matchs.winner = player.name
			for joueur in player.matchs.players:
				if joueur != player and joueur != None:
					player.in_game = False
					joueur.in_game = False
					joueur.loose = True
					#! ADD MATCH HISTORY HERE AND ELO 
					#self.send_history(player.matchs)
					player.matchs.players.remove(joueur)
					self.autPlayer.remove(joueur)
					self.obj_to_remove.append(joueur.paddle)
					try:
						async_to_sync (self.channel_layer.group_send)(self.party_channel_name, {"type": "leave_party", "user_id": joueur.id}) # kick loser
					except Exception as e:
						print(f"#### player_scored Party: ERROR: {e}")
					player.score = 0
					player.matchs.winner = player.name
					self.all_match_end()


	# method for class party
	def	_game_start(self) -> bool:
		return True

	def	_game_stop(self) -> bool:
		return True

	# loop for the game
	def	_game_loop(self) -> bool:
		actual_time = time.time()
		self.tick += 1
		# check if the players is ready to start the game (power of two)
		if self.gameStarted == False and self.activateTimer == True:
			if actual_time > self.timer:
				if __ispoweroftwo__(len(self.playersT)) == True:
					self.gameStarted = True
					self.activateTimer = False
				else:
					self.timer += self.timerupdate
		# check if the game is started
		if self.gameStarted == True:
			if len(self.matchs) == 0:
				self.reset_autPlayer_paddle()
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
				temp_player.paddle = ObjectPaddle(temp_player.name)
				temp_player.paddle.size = vec2(120, 20)
				self.objects.append(temp_player.paddle)
				self.autPlayer.append(temp_player)
			self.playersT.append(temp_player)
			return True
		return False

	# destroy player from list player
	def	_game_leave(self, player: Player) -> bool:
		playerdelet = next((test for test in self.playersT if player.id == test.id), None)
		if playerdelet != None:
			self.playersT.remove(playerdelet)
		return True

	def _game_send_update(self):
 		return True