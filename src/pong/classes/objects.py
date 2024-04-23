
from enum import Enum

from .player import Player
from .math_vec2 import vec2

import uuid
import time
import math
import random
from random import uniform, randint

#
# ENUM SHAPE
#

class Shape(Enum):
	TERRAIN = 0
	PADDLE = 1
	BALL = 2
	BOX = 3
	TEXT = 4

class Collision(Enum):
	NONE		= 0
	BOUNCE		= 1
	STOP		= 2	
	IMMOVABLE	= 3
	

#
# CLASS OBJECT_ABSTRACT
#

class ObjectAbstract:
	def __init__(self):
		self.uuid: uuid 	= str(uuid.uuid4())
		self.controler: str	= None
		
		self.shape			= Shape.BOX
		self.color: str		= '#76ABAE'
		
		self.pos			= vec2(0, 0)
		self.dir			= vec2(0, 0)
		self.vel			= vec2(0, 0)
		self.size			= vec2(16, 16)
		self.rot: float		= 0.0
		
		self.collide		= Collision.IMMOVABLE
		self.camera			= {'username': '', 'mode': 'third_person'}
	
	def control(self, key_values):
		pass

	def update(self):
		pass

	def to_dict(self):
		return {
			"uuid": self.uuid,
			"controler": self.controler,
			"shape": str(self.shape),
			"pos": self.pos.to_dict(),
			"vel": self.vel.to_dict(),
			"size": self.size.to_dict(),
			"rot": self.rot,
			"color": self.color,
			"camera": self.camera,
		}
	
class ObjectTerrain(ObjectAbstract):
	def __init__(self):
		super().__init__()
		self.shape		= Shape.TERRAIN
		self.color		= '#EEEEEE'
		self.size		= vec2(400, 600)
		self.controler	= None
		self.collide	= Collision.NONE

class ObjectPaddle(ObjectAbstract):
	def __init__(self, controler: str):
		super().__init__()
		self.shape		= Shape.PADDLE
		
		random.seed(controler)
		r = lambda: random.randint(190, 220)
		self.color		= '#{:02x}{:02x}{:02x}'.format(r(), 127, r())
		
		self.size		= vec2(32, 23)
		self.collide	= Collision.STOP
		self.controler	= controler
		self.camera		= {'username': controler, 'mode': 'third_person'}
		pass

	def control(self, key_values):
		val_sin = math.sin(self.rot)
		val_cos = math.cos(self.rot)

		direction = vec2(0, 0)
		
		if (key_values.get('w', False)):
			direction.x += +val_sin
			direction.y += +val_cos

		if (key_values.get('s', False)):
			direction.x += -val_sin
			direction.y += -val_cos
		
		if (key_values.get('a', False)):
			direction.x += +val_cos
			direction.y += -val_sin
		
		if (key_values.get('d', False)):
			direction.x += -val_cos
			direction.y += +val_sin

		self.vel = direction * 8
  
		pass

	def update(self):
		self.pos = self.pos + self.vel
		pass

class ObjectBall(ObjectAbstract):
	def __init__(self):
		super().__init__()
		self.shape		= Shape.BALL
		self.color		= '#0066b1'
		self.collide	= Collision.BOUNCE
		self.size		= vec2(40, 40)
		self.rot		= uniform(0, 2 * math.pi)
		self.dir		= vec2(math.sin(self.rot), math.cos(self.rot))
		self.vel		= self.dir * 8
		self.pos		= self.pos * 20

	def update(self):
		self.pos		= self.pos + self.vel
		self.vel		= self.dir * 8
		pass

class ObjectText(ObjectAbstract):
	def __init__(self):
		super().__init__()
		self.shape		= Shape.TEXT
		self.color		= '#EEEEEE'
		self.size		= vec2(10, 0)
		self.controler	= None
		self.collide	= Collision.NONE