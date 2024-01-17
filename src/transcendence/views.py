from django.shortcuts import render

def home_view(request):
    return render(request, "home.html")

def leaderboard_view(request):
    return render(request, "leaderboard.html")