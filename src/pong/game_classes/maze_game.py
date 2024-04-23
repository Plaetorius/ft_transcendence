from ..classes.party import ( Party )
from ..classes.player import ( Player )
from ..classes.objects import ( Shape, Collision, ObjectAbstract)
from ..classes.math_vec2 import ( vec2 )
from random import randint, uniform
from enum import Enum
import random, math, time

# idees :
# - laisser les autres joueurs finir la partie, et mettre une notif player x a fini la partie et le mettre en spectateur
# - si un joueur deco en plein milieu raf, laisser le paddle la ou il est
# - mmetre la cam en premiere personne ou en 3eme si on en a rien a foutre
# - mettre la cam en 0,0 pour les spectateurs
# - si tu rentre apres que lq game ait commence, tu es spectateur
# - si tu rentre avant, tu es joueur
# - mettre un timer avant que la game soit reset (exemple 5min) ? ou juste attendre que tout le monde ait fini / quiter

BOX_SIZE = vec2(20, 20)

class MazePaddle(ObjectAbstract):
	def __init__(self, controler: str):
		super().__init__()
		self.shape		= Shape.PADDLE
		
		random.seed(controler)
		r = lambda: random.randint(190, 220)
		self.color		= '#{:02x}{:02x}{:02x}'.format(r(), 127, r())
		
		self.size		= vec2(4, 4)
		self.collide	= Collision.STOP
		self.controler	= controler
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

		if (key_values.get('q', False)):
			self.rot = self.rot + 0.1

		if (key_values.get('e', False)):
			self.rot = self.rot - 0.1

		self.vel = direction * 8
  
		pass

	def update(self):
		self.pos = self.pos + self.vel
		pass

class Maze(Party):
	def __init__(self):
		super().__init__()
		self.joueurs = []
		self.spectateurs = []
		self.gameStarted = False
		self.timerStart = time.time()
		self.already_joined: dict[str]	= []
		self.maze_size = 15
		self.maze = []

	def generate_terrain2(self):
		self.mid_point = vec2(self.maze_size/ 2, self.maze_size / 2)
		for x in range(self.maze_size):
			for y in range(self.maze_size):
				if self.maze[y][x] == 1:
					wall = ObjectAbstract()
					wall.shape = Shape.BOX
					wall.size = vec2(BOX_SIZE.x, BOX_SIZE.y)
					wall.pos = vec2(x * BOX_SIZE.x, y * BOX_SIZE.y) - self.mid_point * BOX_SIZE
					wall.pos = -wall.pos
					self.objects.append(wall)
				elif self.maze[y][x] == 3:
					wall = ObjectAbstract()
					wall.shape = Shape.BOX
					wall.size = vec2(BOX_SIZE.x, BOX_SIZE.y)
					wall.pos = vec2(x * BOX_SIZE.x, y * BOX_SIZE.y) - self.mid_point * BOX_SIZE
					wall.pos = -wall.pos
					wall.color = '#ff0000'
					self.objects.append(wall)

	# def generate_terrain(self):
	# 	self.mid_point = vec2(self.maze_size / 2, self.maze_size / 2)
	# 	maxed = (self.maze_size / 2) * BOX_SIZE.x

	# 	for x in range(self.maze_size):
	# 		ranger_min = 0
	# 		ranger_max = 0
	# 		for y in range(self.maze_size):
	# 			if self.maze[y][x] == 1:
	# 				ranger_max += 1
	# 			elif self.maze[y][x] == 0 and ranger_max > ranger_min and ranger_max - ranger_min > 1:
	# 				wall = ObjectAbstract()
	# 				wall.shape = Shape.BOX
	# 				wall.size = vec2((ranger_max - ranger_min) * BOX_SIZE.x,  BOX_SIZE.y)
	# 				wall.pos = vec2(y * BOX_SIZE.x, x * BOX_SIZE.y) - self.mid_point * BOX_SIZE
	# 				wall.pos = -wall.pos
	# 				wall.color = '#0066b1'
	# 				self.objects.append(wall)
	# 				print(ranger_max - ranger_min)
	# 				ranger_max = x
	# 				ranger_min = x
	# 			elif ranger_max - ranger_min == 1:
	# 				wall = ObjectAbstract()
	# 				wall.shape = Shape.BOX
	# 				wall.size = vec2(BOX_SIZE.y, BOX_SIZE.x)
	# 				wall.pos = vec2(y * BOX_SIZE.x, x * BOX_SIZE.y) - self.mid_point * BOX_SIZE
	# 				wall.pos = -wall.pos
	# 				wall.color = '#00ff00'
	# 				self.objects.append(wall)
	# 				ranger_max = x
	# 				ranger_min = x
	# 			elif self.maze[y][x] == 3:
	# 				wall = ObjectAbstract()
	# 				wall.shape = Shape.BOX
	# 				wall.size = vec2(BOX_SIZE.x, BOX_SIZE.y)
	# 				wall.pos = vec2(y * BOX_SIZE.x, x * BOX_SIZE.y) - self.mid_point * BOX_SIZE
	# 				wall.pos = -wall.pos
	# 				wall.color = '#ff0000'
	# 				self.objects.append(wall)
	# 				ranger_max = x
	# 				ranger_min = x
	# 	print("------------------------------------------------------------")
	# 	# for y in range(self.maze_size):
	# 	# 	ranger_min = 0
	# 	# 	ranger_max = 0
	# 	# 	for x in range(self.maze_size):
	# 	# 		if self.maze[y][x] == 1: 
	# 	# 			ranger_max += 1
	# 	# 		elif self.maze[y][x] == 0 and ranger_max > ranger_min and ranger_max - ranger_min > 1:
	# 	# 			wall = ObjectAbstract()intin == 1:
	# 	# 			wall = ObjectAbstract()
	# 	# 			wall.shape = Shape.BOX
	# 	# 			wall.size = vec2(BOX_SIZE.y, BOX_SIZE.x)
	# 	# 			wall.pos = vec2(y * BOX_SIZE.x, x * BOX_SIZE.y) - self.mid_point * BOX_SIZE
	# 	# 			wall.pos = -wall.pos
	# 	# 			wall.color = '#00ff00'
	# 	# 			self.objects.append(wall)
	# 	# 			ranger_max = x
	# 	# 			ranger_min = x
	# 	# 		elif self.maze[y][x] == 3:
	# 	# 			wall = ObjectAbstract()
	# 	# 			wall.shape = Shape.BOX
	# 	# 			wall.size = vec2(BOX_SIZE.x, BOX_SIZE.y)
	# 	# 			wall.pos = vec2(y * BOX_SIZE.x, x * BOX_SIZE.y) - self.mid_point * BOX_SIZE
	# 	# 			wall.pos = -wall.pos
	# 	# 			wall.color = '#ff0000'
	# 	# 			self.objects.append(wall)
	# 	# 			ranger_max = x
	# 	# 			ranger_min = x
	# 	#create contour	walls
	# 	wall = ObjectAbstract()
	# 	wall.shape = Shape.BOX
	# 	wall.color = '#8b5c29'
	# 	wall.size = vec2(BOX_SIZE.y * self.maze_size, BOX_SIZE.x) # haut
	# 	wall.pos = vec2(0, maxed)
	# 	self.objects.append(wall)
	# 	wall = ObjectAbstract()
	# 	wall.shape = Shape.BOX
	# 	wall.color = '#8b5c29'
	# 	wall.size = vec2(BOX_SIZE.y * self.maze_size,BOX_SIZE.x) # bas
	# 	wall.pos = vec2(0, -maxed)
	# 	self.objects.append(wall)
	# 	wall = ObjectAbstract()
	# 	wall.shape = Shape.BOX
	# 	wall.color = '#8b5c29'
	# 	wall.size = vec2( BOX_SIZE.y , self.maze_size * BOX_SIZE.x) # gauche
	# 	wall.pos = vec2(maxed, 0)
	# 	self.objects.append(wall)
	# 	wall = ObjectAbstract()
	# 	wall.shape = Shape.BOX
	# 	wall.color = '#8b5c29'
	# 	wall.size = vec2( BOX_SIZE.y, self.maze_size * BOX_SIZE.x)	# droite
	# 	wall.pos = vec2(-maxed, 0)
	# 	self.objects.append(wall)

	def createpaddle(self, player):
		paddle = MazePaddle(player.name)
		paddle.color = '#ff0000'
		paddle.pos = vec2(10, 10)
		self.objects.append(paddle) 


	def generate_maze(self, maze, x, y):
		pos = vec2(x, y)
		maze[pos.x][pos.y] = 2
		history = [pos]
		directions = [vec2(2, 0), vec2(0, 2), vec2(-2, 0), vec2(0, -2)]

		furthest_pos = vec2(0, 0)
		max_len = 0

		while len(history):
			possible_directions = []

			# Check all possible cells
			for i in range(4):
				new_pos = pos + directions[i]
				if new_pos.x > 0 and new_pos.x < self.maze_size and new_pos.y > 0 and new_pos.y < self.maze_size and maze[new_pos.x][new_pos.y] == 1:
					possible_directions.append(directions[i])

			# If moving is possible
			if (len(possible_directions) > 0):
				random_direction = random.choice(possible_directions)
				temp_pos = pos + random_direction / 2
				pos = pos + random_direction
				history.append(pos)
				maze[int(temp_pos.x)][int(temp_pos.y)] = 0
				maze[pos.x][pos.y] = 0
				if (len(history) > max_len):
					max_len = len(history)
					furthest_pos = pos
			else:
				history.pop()
				if len(history) != 0:
					pos = history[-1]
		
		maze[furthest_pos.x][furthest_pos.y] = 3

		return maze
	
	def create_map(self):
		# Create the maze
		# 0 = path
		# 1 = wall
		# 2 = start
		# 3 = end
		self.maze = []
		for i in range(self.maze_size):
			self.maze.append([])
			for j in range(self.maze_size):
				self.maze[i].append(1)
		self.maze = self.generate_maze(self.maze, round((self.maze_size - 1) / 2), round((self.maze_size - 1) / 2))
		for i in range(self.maze_size):
			print(self.maze[i])
		self.generate_terrain2()
		# self.generate_terrain()

	def reset_game(self):
		self.joueurs = []
		self.spectateurs = []
		self.gameStarted = False
		self.timerStart = time.time()
		self.already_joined = []
		self.obj_to_remove.extend(self.objects)


	def	_game_start(self) -> bool:
		return True

	def	_game_stop(self) -> bool:
		return True

	def	_game_loop(self) -> bool:
		return True
	
	def	_game_join(self, player: Player) -> bool:
		if (not (player.name in self.already_joined)):
			if self.gameStarted == True:
				self.spectateurs.append(player)
			else:
				self.joueurs.append(player)
				self.createpaddle(player)
			self.already_joined.append(player.name)
		if (len(self.joueurs) == 1):
			self.gameStarted = True
			self.create_map()
		return True

	def	_game_leave(self, player: Player) -> bool:
		self.reset_game()
		return True

	# Game send update
	def _game_send_update(self):
		return True




# [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
# [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1]
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1]
# [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1]
# [1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1]
# [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1]
# [1, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 1, 0, 1]
# [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1]
# [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1]
# [1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1]
# [1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1]
# [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1]
# [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1]
# [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
