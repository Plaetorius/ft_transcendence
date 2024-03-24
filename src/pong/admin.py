# pong/admin.py
# Register your models here.

from django.contrib import admin
from .models import PongGame

admin.site.register(PongGame)