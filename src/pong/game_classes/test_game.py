
from ..classes.party import ( Party )
from ..classes.player import ( Player )
from ..classes.objects import ( Shape, ObjectAbstract, ObjectBall, ObjectTerrain, ObjectPaddle)

from ..classes.math_vec2 import ( vec2 )

import uuid
import time

class	TestParty(Party):
	def	__init__(self):
		super().__init__()
		self.name = "TestParty"
		self.max_players = 6
		
		self.S_PER_UPDATE = 1.0 / 4.0
		
		for i in range(10):
			terrain = ObjectTerrain()
			terrain.size = vec2(200, 200)
			terrain.pos.y = -i * 210
			self.objects.append(terrain)

	def	_game_start(self) -> bool:
		print("TestParty: _game_start")
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
