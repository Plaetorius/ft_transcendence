from django.contrib import admin
from .models import User, MatchHistory, ChatMessage, Friendship, Achievement, FriendRequest

admin.site.register(User)
admin.site.register(MatchHistory)
admin.site.register(ChatMessage)
admin.site.register(Friendship)
admin.site.register(Achievement)
admin.site.register(FriendRequest)
