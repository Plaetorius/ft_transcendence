
from enum import Enum

from .player import Player
from .math_vec2 import vec2

import uuid
import math
from random import uniform

#
# ENUM SHAPE
#

class Shape(Enum):
	TERRAIN = 0
	PADDLE = 1
	BALL = 2
	BOX = 3

#
# CLASS OBJECT_ABSTRACT
#

class ObjectAbstract:
	def __init__(self):
		self.uuid: uuid = str(uuid.uuid4())
		self.controler: str = None
		
		self.shape = Shape.PADDLE
		self.pos = vec2(0, 0)
		self.vel = vec2(0, 0)
		self.size = vec2(16, 16)
		self.rot = 0
	
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
			"rot": self.rot
		}

class ObjectPaddle(ObjectAbstract):
	def __init__(self, controler: str):
		super().__init__()
		self.shape = Shape.PADDLE
		self.size = vec2(32, 8)
		self.controler = controler

	def control(self, key_values):
		val_sin = math.sin(self.rot)
		val_cos = math.cos(self.rot)

		direction = vec2(0, 0)
		if (key_values.get('z', False)):
			direction.x += +val_sin
			direction.y += +val_cos

		if (key_values.get('s', False)):
			direction.x += -val_sin
			direction.y += -val_cos
		
		if (key_values.get('q', False)):
			direction.x += +val_cos
			direction.y += -val_sin
		
		if (key_values.get('d', False)):
			direction.x += -val_cos
			direction.y += +val_sin

		# normalize velocity to value
		# disp = direction.__abs__()
		# if (disp > 1.0):
		# 	direction = direction / disp

		self.vel = direction * 5

		if (key_values.get('a', False)):
			self.rot = self.rot + 0.1

		if (key_values.get('e', False)):
			self.rot = self.rot - 0.1
		pass

	def update(self):
		self.pos = self.pos + self.vel
		pass

class ObjectBall(ObjectAbstract):
	def __init__(self):
		super().__init__()
		self.shape = Shape.BALL
		self.size = vec2(10, 10)
		self.rot = uniform(0, 2 * math.pi)
		self.vel = vec2(math.sin(self.rot), math.cos(self.rot)) * 5

	def update(self):
		if (self.pos.x < -200 + 5):
			self.pos.x = -200 + 5
			self.vel.x = -self.vel.x
		if (self.pos.x > 200 - 5):
			self.pos.x = 200 - 5
			self.vel.x = -self.vel.x
		if (self.pos.y < -300 + 5):
			self.pos.y = -300 + 5
			self.vel.y = -self.vel.y
		if (self.pos.y > 300 - 5):
			self.pos.y = 300 - 5
			self.vel.y = -self.vel.y

		self.pos = self.pos + self.vel
		pass
