# users/admin.py
from django.contrib import admin
from .models import User, MatchHistory, Friendship, Achievement, BlockedUser, OAuthCred, PlayerMatchHistory

admin.site.register(User)
admin.site.register(MatchHistory)
admin.site.register(Friendship)
admin.site.register(Achievement)
admin.site.register(BlockedUser)
admin.site.register(OAuthCred)
admin.site.register(PlayerMatchHistory)