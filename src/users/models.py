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
    elo = models.IntegerField(default=1000)

    def __str__(self):
        return f"User: {self.username} Id: {self.id}"

# Match history Class
class MatchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game_type = models.CharField(max_length=100)
    score = models.IntegerField()
    # TODO Change to the real Game class
    date_played = models.DateTimeField(auto_now_add=True)

# Private Message Class
class PrivateMessage(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Private Message: {self.sender} -> {self.receiver}: {self.image}"

# Friendship Class
class Friendship(models.Model):
    friend1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend1', on_delete=models.CASCADE)
    friend2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('friend1', 'friend2')
    
    def __str__(self):
        return f"Friendship: {self.friend1} -> {self.friend2}"

# TODO remove
# Friend Request Class
class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="friend_request_sent", on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="friend_request_received", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"FriendshipRequest: {self.from_user} -> {self.to_user}"


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