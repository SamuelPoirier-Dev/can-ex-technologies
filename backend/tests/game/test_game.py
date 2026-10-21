import pytest

from app.game.board import SALARY, STARTING_MONEY, Board, Square
from app.game.errors import (
    GameAlreadyStarted,
    GameFull,
    GameNotInProgress,
    InvalidPlayerCount,
    InvalidRoll,
    NotYourTurn,
)
from app.game.events import (
    Bankrupted,
    GameWon,
    Moved,
    PropertyBought,
    RentPaid,
    SalaryCollected,
)
from app.game.models import Game, GameStatus

# Small board so positions and amounts stay easy to follow.
START, CHEAP, EMPTY, PRICEY = 0, 1, 2, 3
BOARD = Board(
    squares=(
        Square("Start"),
        Square("Cheap", price=100, rent=10),
        Square("Empty"),
        Square("Pricey", price=300, rent=50),
    )
)


def started_game(player_count: int = 2) -> Game:
    game = Game(id="g1", max_players=player_count, board=BOARD)
    for i in range(player_count):
        game.add_player(f"Player {i + 1}")
    return game


# --- Lobby ---


@pytest.mark.parametrize("count", [1, 5])
def test_rejects_player_count_outside_2_to_4(count: int) -> None:
    with pytest.raises(InvalidPlayerCount):
        Game(id="g1", max_players=count)


def test_waits_until_full_then_starts() -> None:
    game = Game(id="g1", max_players=3)

    game.add_player("Alice")
    game.add_player("Bob")
    assert game.status is GameStatus.WAITING

    game.add_player("Carol")
    assert game.status is GameStatus.IN_PROGRESS
    assert game.current_player.name == "Alice"


def test_new_players_start_on_start_square_with_starting_money() -> None:
    game = Game(id="g1", max_players=2)

    player = game.add_player("Alice")

    assert player.position == START
    assert player.money == STARTING_MONEY
    assert not player.is_bankrupt


def test_rejects_join_once_started() -> None:
    game = started_game(2)

    with pytest.raises(GameAlreadyStarted):
        game.add_player("Late")


def test_rejects_join_when_full() -> None:
    # A full game is always started, so fill it by hand to check the guard alone.
    game = Game(id="g1", max_players=2)
    game.add_player("Alice")
    game.add_player("Bob")
    game.status = GameStatus.WAITING

    with pytest.raises(GameFull):
        game.add_player("Carol")


# --- Turn guards ---


def test_cannot_play_before_game_starts() -> None:
    game = Game(id="g1", max_players=2)
    alice = game.add_player("Alice")

    with pytest.raises(GameNotInProgress):
        game.play_turn(alice.id, 1)


def test_cannot_play_out_of_turn() -> None:
    game = started_game(2)

    with pytest.raises(NotYourTurn):
        game.play_turn("p2", 1)


@pytest.mark.parametrize("roll", [0, 7])
def test_rejects_impossible_roll(roll: int) -> None:
    game = started_game(2)

    with pytest.raises(InvalidRoll):
        game.play_turn("p1", roll)


def test_turn_passes_to_next_player_and_wraps_around() -> None:
    game = started_game(2)

    game.play_turn("p1", 2)
    assert game.current_player.id == "p2"

    game.play_turn("p2", 2)
    assert game.current_player.id == "p1"


# --- Movement and salary ---


def test_moves_forward_by_roll() -> None:
    game = started_game(2)

    events = game.play_turn("p1", 2)

    assert game.player("p1").position == EMPTY
    assert events == [Moved("p1", 2, START, EMPTY)]


def test_wraps_around_board_and_collects_salary_when_passing_start() -> None:
    game = started_game(2)
    game.player("p1").position = PRICEY

    events = game.play_turn("p1", 3)

    assert game.player("p1").position == EMPTY
    assert SalaryCollected("p1", SALARY) in events
    assert game.player("p1").money == STARTING_MONEY + SALARY


def test_collects_salary_when_landing_on_start() -> None:
    game = started_game(2)
    game.player("p1").position = PRICEY

    events = game.play_turn("p1", 1)

    assert game.player("p1").position == START
    assert events == [Moved("p1", 1, PRICEY, START), SalaryCollected("p1", SALARY)]


def test_no_salary_without_passing_start() -> None:
    game = started_game(2)

    game.play_turn("p1", 2)

    assert game.player("p1").money == STARTING_MONEY


# --- Buying ---


def test_buys_unowned_property() -> None:
    game = started_game(2)

    events = game.play_turn("p1", 1)

    assert PropertyBought("p1", CHEAP, 100) in events
    assert game.owners[CHEAP] == "p1"
    assert game.properties_of("p1") == [CHEAP]
    assert game.player("p1").money == STARTING_MONEY - 100


def test_does_not_buy_when_money_is_short() -> None:
    game = started_game(2)
    game.player("p1").money = 99

    events = game.play_turn("p1", 1)

    assert CHEAP not in game.owners
    assert game.player("p1").money == 99
    assert events == [Moved("p1", 1, START, CHEAP)]


def test_buys_when_money_exactly_matches_price() -> None:
    game = started_game(2)
    game.player("p1").money = 100

    game.play_turn("p1", 1)

    assert game.owners[CHEAP] == "p1"
    assert game.player("p1").money == 0


def test_nothing_happens_on_empty_square() -> None:
    game = started_game(2)

    events = game.play_turn("p1", 2)

    assert events == [Moved("p1", 2, START, EMPTY)]
    assert game.owners == {}


# --- Rent ---


def test_pays_rent_to_owner() -> None:
    game = started_game(2)
    game.owners[CHEAP] = "p2"

    events = game.play_turn("p1", 1)

    assert RentPaid("p1", "p2", CHEAP, 10) in events
    assert game.player("p1").money == STARTING_MONEY - 10
    assert game.player("p2").money == STARTING_MONEY + 10


def test_nothing_happens_on_own_property() -> None:
    game = started_game(2)
    game.owners[CHEAP] = "p1"

    events = game.play_turn("p1", 1)

    assert events == [Moved("p1", 1, START, CHEAP)]
    assert game.player("p1").money == STARTING_MONEY


def test_paying_exact_rent_leaves_player_in_game() -> None:
    game = started_game(2)
    game.owners[CHEAP] = "p2"
    game.player("p1").money = 10

    game.play_turn("p1", 1)

    assert game.player("p1").money == 0
    assert not game.player("p1").is_bankrupt
    assert game.status is GameStatus.IN_PROGRESS


# --- Bankruptcy and winner ---


def test_bankrupt_player_hands_remaining_money_and_frees_properties() -> None:
    game = started_game(3)
    game.owners[PRICEY] = "p2"
    game.owners[CHEAP] = "p1"
    game.player("p1").money = 30
    game.player("p1").position = EMPTY

    events = game.play_turn("p1", 1)

    assert events == [
        Moved("p1", 1, EMPTY, PRICEY),
        RentPaid("p1", "p2", PRICEY, 30),
        Bankrupted("p1", "p2"),
    ]
    assert game.player("p1").is_bankrupt
    assert game.player("p1").money == 0
    assert game.player("p2").money == STARTING_MONEY + 30
    assert game.owners == {PRICEY: "p2"}
    assert game.status is GameStatus.IN_PROGRESS


def test_bankrupt_player_is_skipped_in_turn_order() -> None:
    game = started_game(3)
    game.owners[PRICEY] = "p1"
    game.player("p2").money = 0
    game.player("p2").position = EMPTY

    game.play_turn("p1", 2)  # p1 lands on Empty
    game.play_turn("p2", 1)  # p2 lands on p1's Pricey and goes bankrupt
    game.play_turn("p3", 2)

    assert game.current_player.id == "p1"
    game.play_turn("p1", 2)
    assert game.current_player.id == "p3"


def test_last_player_standing_wins() -> None:
    game = started_game(2)
    game.owners[CHEAP] = "p2"
    game.player("p1").money = 5

    events = game.play_turn("p1", 1)

    assert events[-2:] == [Bankrupted("p1", "p2"), GameWon("p2")]
    assert game.status is GameStatus.FINISHED
    assert game.winner_id == "p2"


def test_no_turn_can_be_played_after_game_ends() -> None:
    game = started_game(2)
    game.owners[CHEAP] = "p2"
    game.player("p1").money = 5
    game.play_turn("p1", 1)

    with pytest.raises(GameNotInProgress):
        game.play_turn("p2", 1)


def test_turn_events_are_appended_to_game_log() -> None:
    game = started_game(2)

    first = game.play_turn("p1", 1)
    second = game.play_turn("p2", 2)

    assert game.events == first + second
