
from enum import Enum

from .player import Player
from .math_vec2 import vec2

import uuid

#
# ENUM SHAPE
#

class Shape(Enum):
	PADDLE = 1
	SPHERE = 2
	BOX = 3

#
# CLASS OBJECT_ABSTRACT
#

class ObjectAbstract:
	def __init__(self):
		self.uuid: uuid = str(uuid.uuid4())
		self.controler: Player = None
		
		self.shape = Shape.PADDLE
		self.pos = vec2(0, 0)
		self.vel = vec2(0, 0)
		self.rot = 0
	
	def to_dict(self):
		return {
			"uuid": self.uuid,
			"controler": self.controler.to_dict() if self.controler != None else None,
			"shape": str(self.shape),
			"pos": [self.pos.x, self.pos.y],
			"vel": [self.vel.x, self.vel.y],
			"rot": self.rot
		}
