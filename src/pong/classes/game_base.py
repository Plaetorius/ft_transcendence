
from .player import Player
from .objects import ( ObjectAbstract, Shape )
from .math_vec2 import vec2

#
# CLASS GAMEBASE
#

class GameBase:
	def __init__(self):
		self.initialised = False
		self.started = False
		self.terrain_size = vec2(600, 800)
		self.objects = [] # list of all objects in the game (paddles, ball, etc...)
	
	def	init_game(self) -> bool:
		if (self.initialised == True):
			print(f"	PONGGAME: Game already initialised")
			return False
		if (len(self.players) < self.max_players):
			print(f"	PONGGAME: Not enough players to initialise the party n°{str(self.party_uuid)}")
			return False
		
		paddle_p1 = ObjectAbstract()
		paddle_p1.controler = self.players[0]
		paddle_p1.shape = Shape.PADDLE
		paddle_p1.pos = vec2(self.terrain_size.x / 2, 0)
		paddle_p1.rot = 0, 0
		self.objects.append(paddle_p1)
		
		paddle_p2 = ObjectAbstract()
		paddle_p2.controler = self.players[1]
		paddle_p2.shape = Shape.PADDLE
		paddle_p2.pos = vec2(self.terrain_size.x / 2, self.terrain_size.y)
		paddle_p2.rot = 0, 0
		self.objects.append(paddle_p2)
		
		ball = ObjectAbstract()
		ball.controler = None
		ball.shape = Shape.SPHERE
		ball.pos = vec2(self.terrain_size.x / 2, self.terrain_size.y / 2)
		ball.rot = 0, 0
		self.objects.append(ball)
		
		self.initialised = True
		
		return True
	
	def	start_game(self) -> bool:
		if (self.started == True):
			return False
		self.started = True
		print(f"	PONGGAME: Game n°{str(self.uuid)} started")
		return True
	
	def	stop_game(self) -> bool:
		if (self.started == False):
			return False
		self.started = True
		print(f"	PONGGAME: Game n°{str(self.uuid)} stopped")
		return True
	
	def to_dict(self) -> dict:
		return {
			"players":		[self.players],
			"max_players":	self.max_players,
			"initialised":	self.initialised,
			"started":		self.started,
			"terrain_size":	self.terrain_size,
			"objects":		[self.objects]
		}
