# users/elo.py
from .models import User

def get_k(elo: int) -> int:
    if elo < 1000:
        return 32
    elif elo < 1500:
        return 28
    elif elo < 2000:
        return 24
    elif elo < 2500:
        return 20
    return 16

def game_result(winner: User, looser: User):
    print(f"#### Initial ELOs: {winner.username} {winner.elo} vs {looser.username} {looser.elo}")

    winner_expected = 1 / (1 + 10 ** ((looser.elo - winner.elo) / 400))
    looser_expected = 1 - winner_expected  #

    winner.elo += get_k(winner.elo) * (1 - winner_expected)  # Winner's result is 1 since they won
    looser.elo += get_k(looser.elo) * (0 - looser_expected)  # Loser's result is 0 since they lost

    print(f"#### Updated ELOs: {winner.username} {winner.elo} vs {looser.username} {looser.elo}")

    winner.save()
    looser.save()

    return [winner.elo, looser.elo]
