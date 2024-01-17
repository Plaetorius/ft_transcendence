# pong/views.py
from django.shortcuts import render

def games_view(request):
    return render(request, 'pong/games.html')