# chat/models.py
from django.db import models
from django.conf import settings

class ChatRoom(models.Model):
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="members")
    is_direct_message = models.BooleanField(default=False)
    def __str__(self):
        return f'Chat Room {self.id}'

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name="chatroom", on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sender", on_delete=models.CASCADE)
    content = models.TextField() #TODO maybe add a size limit?
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content