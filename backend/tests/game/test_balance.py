"""Guard against economy settings where nobody ever goes bankrupt."""

import random

import pytest

from app.game.models import Game, GameStatus

MAX_TURNS = 200


def play_random_game(seed: int) -> Game:
    rng = random.Random(seed)
    game = Game(id="g1", max_players=2)
    game.add_player("Alice")
    game.add_player("Bob")

    for _ in range(MAX_TURNS):
        if game.status is not GameStatus.IN_PROGRESS:
            break
        game.play_turn(game.current_player.id, rng.randint(1, 6))
    return game


@pytest.mark.parametrize("seed", range(20))
def test_two_player_game_ends_on_default_board(seed: int) -> None:
    game = play_random_game(seed)

    assert game.status is GameStatus.FINISHED
    assert game.winner_id is not None
