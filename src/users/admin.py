# users/admin.py
from django.contrib import admin
from .models import User, MatchHistory, PrivateMessage, Friendship, Achievement, FriendRequest, BlockedUser

admin.site.register(User)
admin.site.register(MatchHistory)
admin.site.register(PrivateMessage)
admin.site.register(Friendship)
admin.site.register(Achievement)
admin.site.register(FriendRequest)
admin.site.register(BlockedUser)