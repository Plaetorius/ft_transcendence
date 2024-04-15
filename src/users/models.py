# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.deconstruct import deconstructible
import os

# User class, implementing AbstractUser for greater flex
class User(AbstractUser):
    username = models.CharField(
        max_length=20,
        unique=True,
        error_messages={
            'unique': "This username is already in use."
        },
    )
    bio = models.TextField(max_length=500, blank=True, default='')
    profile_picture = models.ImageField(
		upload_to='profile_pictures/',
		blank=True,
		null=True,
		default="profile_pictures/default.jpg"
	)
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        error_messages={
            'unique': "This email is already in use."
        },
    )
    first_name = models.CharField(max_length=30, blank=True, default='')
    last_name = models.CharField(max_length=50, blank=True, default='')
    elo = models.IntegerField(default=1000)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True) # already in model
    oauth = models.BooleanField(default=False)


    def __str__(self):
        return f"User: {self.username} Id: {self.id}"

# Match history Class
class MatchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game_type = models.CharField(max_length=100)
    score = models.IntegerField()
    # TODO Change to the real Game class
    date_played = models.DateTimeField(auto_now_add=True)


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