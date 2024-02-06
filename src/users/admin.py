# users/admin.py
from django.contrib import admin
from .models import User, MatchHistory, Friendship, Achievement, BlockedUser

admin.site.register(User)
admin.site.register(MatchHistory)
admin.site.register(Friendship)
admin.site.register(Achievement)
admin.site.register(BlockedUser)
