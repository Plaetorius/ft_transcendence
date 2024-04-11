
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
		self.uuid: uuid = uuid.uuid4()
		self.controler: Player = None
		
		self.shape = Shape.PADDLE
		self.pos = vec2(0, 0)
		self.vel = vec2(0, 0)
		self.rot = vec2(0, 0)
