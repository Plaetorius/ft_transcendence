# pong/models.py
from django.db import models
from django.conf import settings

# Create your models here.

# pong/models.py

class PongGame(models.Model):
	players = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='pong_games')
	# Add other fields and methods as needed

	name = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name

	def get_players(self):
		return self.players.all()

	def add_player(self, player):
		self.players.add(player)

	def remove_player(self, player):
		self.players.remove(player)

	def start_game(self):
		# Logic to start the game
		pass

	def end_game(self):
		# Logic to end the game
		pass

	def update_score(self, player, score):
		# Logic to update the score for a player
		pass

	def get_winner(self):
		# Logic to determine the winner of the game
		pass