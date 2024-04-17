
from ..classes.party import ( Party )
from ..classes.player import ( Player )
from ..classes.objects import ( Shape, ObjectAbstract, ObjectBall, ObjectTerrain, ObjectPaddle)

import uuid
import time

class	PongParty(Party):
	def	__init__(self):
		super().__init__()
		self.name = "PongParty"
		self.max_players = 2
		
		terrain = ObjectTerrain()
		self.objects.append(terrain)

		for i in range(10):
			ball = ObjectBall()
			self.objects.append(ball)

	def	_game_start(self) -> bool:
		print("PongParty: _game_start")
		return True

	def	_game_stop(self) -> bool:
		return True

	def	_game_loop(self) -> bool:
		print(f"####	Party: Looping party {self.uuid} at {time.time()} ...")
		return True
	
	def	_game_join(self, player: Player) -> bool:
		self.objects.append(ObjectPaddle(player.name))
		
		return True

	def	_game_leave(self, player: Player) -> bool:
		return True

	def _game_send_update(self):
		return True
