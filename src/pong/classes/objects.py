
from django.conf import settings
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

class object_abstract:
	uuid:		uuid.UUID
	controler:	Player
	
	shape:		Shape
	pos:		vec2
	vel:		vec2
	rot:		float
	
	def __init__(self):
		self.id = uuid.uuid4()
		self.controler = None
		self.shape = Shape.PADDLE
		self.pos = 0, 0
		self.vel = 0, 0
		self.rot = 0, 0
		
	
