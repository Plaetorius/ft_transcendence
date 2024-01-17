# users/elo.py
from .models import User

def get_k(elo: int) -> int:
    if elo < 1000:
        return 32
    elif elo >= 1000 and elo < 1500:
        return 28
    elif elo >= 1500 and elo < 2000:
        return 24
    elif elo >= 2000 and elo < 2500:
        return 20
    return 16

def game_result(winner: User, looser: User, float: result):
    winner_exp = 1 / (1 + 10 ** (looser.elo - winner.elo) / 400)
    looser_exp = 1 / (1 + 10 ** (winner.elo - looser.elo) / 400)
    winner.elo += get_k(winner.elo) * (0 + result - winner_exp) # the 0 is here so it looks nicer
    looser.elo += get_k(looser.elo) * (1 - result - looser_exp)
    winner.save()
    looser.save()

