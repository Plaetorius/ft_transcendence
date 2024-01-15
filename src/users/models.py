from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


# User class, implementing AbstractUser for greater flex
class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, default="profile_pictures/default.jpg")
    email = models.EmailField(unique=True, blank=False, null=False)

# Match history Class
class MatchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game_type = models.CharField(max_length=100)
    score = models.IntegerField()
    date_played = models.DateTimeField(auto_now_add=True)

# Chat Message Class
class ChatMessage(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

# Friendship Class
class Friendship(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships', on_delete=models.CASCADE)
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friends', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'friend')

# Friend Request Class
class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="friend_request_sent", on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="friend_request_received", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('from_user', 'to_user')


# Blocked User Class
class BlockedUser(models.Model):
    blocker = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='blocker', on_delete=models.CASCADE)
    blocked = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='blocked_users', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('blocker', 'blocked')

# Achievement Class
class Achievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    achieved_on = models.DateTimeField(auto_now_add=True)