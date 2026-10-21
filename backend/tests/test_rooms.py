import pytest

from app.game.models import GameStatus
from app.rooms import CODE_ALPHABET, CODE_LENGTH, GameNotFound, InvalidToken, RoomRegistry


def test_created_room_has_readable_code_and_waiting_game() -> None:
    registry = RoomRegistry()

    room = registry.create(max_players=2)

    assert len(room.game.id) == CODE_LENGTH
    assert set(room.game.id) <= set(CODE_ALPHABET)
    assert room.game.status is GameStatus.WAITING


def test_codes_are_unique() -> None:
    registry = RoomRegistry()

    codes = {registry.create(max_players=2).game.id for _ in range(200)}

    assert len(codes) == 200


def test_get_is_case_insensitive() -> None:
    registry = RoomRegistry()
    room = registry.create(max_players=2)

    assert registry.get(room.game.id.lower()) is room


def test_get_unknown_code_raises() -> None:
    with pytest.raises(GameNotFound):
        RoomRegistry().get("NOPE42")


def test_join_returns_distinct_tokens_mapped_to_players() -> None:
    room = RoomRegistry().create(max_players=2)

    alice, alice_token = room.join("Alice")
    bob, bob_token = room.join("Bob")

    assert alice_token != bob_token
    assert room.player_id_for(alice_token) == alice.id
    assert room.player_id_for(bob_token) == bob.id


@pytest.mark.parametrize("token", [None, "forged"])
def test_unknown_token_is_rejected(token: str | None) -> None:
    room = RoomRegistry().create(max_players=2)
    room.join("Alice")

    with pytest.raises(InvalidToken):
        room.player_id_for(token)
