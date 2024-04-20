# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


# User class, implementing AbstractUser for greater flex
class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        error_messages={
            'unique': "A user with that username already exists"
        },
    )
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, default="profile_pictures/default.jpg")
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        error_messages={
            'unique': "A user with that email already exists."
        },
    )
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    elo = models.FloatField(default=1000)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True) # already in model
    oauth = models.BooleanField(default=False)
    # history = models.ManyToManyField(MatchHistory, blank=True)


    def __str__(self):
        return f"User: {self.username} Id: {self.id}"

# Match history Class
class MatchHistory(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)									# User who played the game
	openent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='opponent')		# Opponent
	game_type = models.CharField("RANKED", max_length=100)															# Ranked or not										
	user_score = models.IntegerField()																				# user score of the game
	opponent_score = models.IntegerField()																			# opponent score of the game
	win = models.BooleanField()																						# if the user won							
	user_elo = models.IntegerField()																				# user elo win/loose this game
	opponent_elo = models.IntegerField()																			# opponent elo win/loose this game						
	date_played = models.DateTimeField(auto_now_add=True)															# date of the game


# Friendship Class
class Friendship(models.Model):
    friend1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend1', on_delete=models.CASCADE)
    friend2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('friend1', 'friend2')
    
    def __str__(self):
        return f"Friendship: {self.friend1} -> {self.friend2}"


# Blocked User Class
class BlockedUser(models.Model):
    blocker = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='blocker', on_delete=models.CASCADE)
    blocked = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='blocked', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Blocker: {self.blocker} -> Blocked: {self.blocked}"

# Achievement Class
class Achievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    achieved_on = models.DateTimeField(auto_now_add=True)