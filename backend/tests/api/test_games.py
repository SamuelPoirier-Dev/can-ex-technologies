from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api.routes import get_dice
from app.game.board import DEFAULT_BOARD, STARTING_MONEY
from app.main import create_app

FIXED_ROLL = 1  # Lands on square 1, a property.


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_dice] = lambda: lambda: FIXED_ROLL
    with TestClient(app) as test_client:
        yield test_client


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_game(client: TestClient, max_players: int = 2, name: str = "Alice") -> dict:
    response = client.post(
        "/api/games", json={"max_players": max_players, "player_name": name}
    )
    assert response.status_code == 201
    return response.json()


def join_game(client: TestClient, code: str, name: str = "Bob") -> dict:
    response = client.post(f"/api/games/{code}/players", json={"player_name": name})
    assert response.status_code == 201
    return response.json()


def started_game(client: TestClient) -> tuple[str, str, str]:
    """Returns (code, alice_token, bob_token) for a started 2-player game."""
    alice = create_game(client)
    code = alice["game"]["id"]
    bob = join_game(client, code)
    return code, alice["token"], bob["token"]


# --- Create / join / read ---


def test_creator_joins_the_new_game(client: TestClient) -> None:
    created = create_game(client, max_players=3)

    game = created["game"]
    assert created["player_id"] == "p1"
    assert created["token"]
    assert game["status"] == "waiting"
    assert game["max_players"] == 3
    assert [p["name"] for p in game["players"]] == ["Alice"]
    assert game["current_player_id"] is None


def test_game_starts_when_last_player_joins(client: TestClient) -> None:
    created = create_game(client)

    joined = join_game(client, created["game"]["id"])

    assert joined["player_id"] == "p2"
    assert joined["game"]["status"] == "in_progress"
    assert joined["game"]["current_player_id"] == "p1"


def test_get_game_returns_full_state(client: TestClient) -> None:
    code = create_game(client)["game"]["id"]

    response = client.get(f"/api/games/{code}")

    assert response.status_code == 200
    game = response.json()
    assert len(game["board"]) == len(DEFAULT_BOARD)
    assert game["board"][1]["price"] == DEFAULT_BOARD[1].price
    assert game["players"][0]["money"] == STARTING_MONEY


def test_state_never_exposes_tokens(client: TestClient) -> None:
    code, alice_token, bob_token = started_game(client)

    body = client.get(f"/api/games/{code}").text

    assert alice_token not in body
    assert bob_token not in body


def test_unknown_game_returns_404(client: TestClient) -> None:
    assert client.get("/api/games/NOPE42").status_code == 404
    assert (
        client.post("/api/games/NOPE42/players", json={"player_name": "Bob"}).status_code
        == 404
    )


def test_joining_a_started_game_returns_409(client: TestClient) -> None:
    code, _, _ = started_game(client)

    response = client.post(f"/api/games/{code}/players", json={"player_name": "Carol"})

    assert response.status_code == 409


@pytest.mark.parametrize(
    "body",
    [
        {"max_players": 1, "player_name": "Alice"},
        {"max_players": 5, "player_name": "Alice"},
        {"max_players": 2, "player_name": "   "},
        {"max_players": 2},
    ],
)
def test_invalid_create_request_returns_422(client: TestClient, body: dict) -> None:
    assert client.post("/api/games", json=body).status_code == 422


# --- Turns ---


def test_playing_a_turn_returns_events_and_new_state(client: TestClient) -> None:
    code, alice_token, _ = started_game(client)

    response = client.post(f"/api/games/{code}/turns", headers=auth(alice_token))

    assert response.status_code == 200
    body = response.json()
    price = DEFAULT_BOARD[1].price
    assert body["events"] == [
        {"type": "moved", "player_id": "p1", "roll": 1, "from_position": 0, "to_position": 1},
        {"type": "property_bought", "player_id": "p1", "position": 1, "price": price},
    ]
    alice = body["game"]["players"][0]
    assert alice["money"] == STARTING_MONEY - price
    assert alice["properties"] == [1]
    assert body["game"]["board"][1]["owner_id"] == "p1"
    assert body["game"]["current_player_id"] == "p2"
    assert body["game"]["events"] == body["events"]


def test_playing_out_of_turn_returns_409(client: TestClient) -> None:
    code, _, bob_token = started_game(client)

    response = client.post(f"/api/games/{code}/turns", headers=auth(bob_token))

    assert response.status_code == 409


def test_playing_before_start_returns_409(client: TestClient) -> None:
    created = create_game(client)

    response = client.post(
        f"/api/games/{created['game']['id']}/turns", headers=auth(created["token"])
    )

    assert response.status_code == 409


def test_playing_without_token_returns_401(client: TestClient) -> None:
    code, _, _ = started_game(client)

    assert client.post(f"/api/games/{code}/turns").status_code == 401


def test_token_from_another_game_returns_401(client: TestClient) -> None:
    code, _, _ = started_game(client)
    _, other_token, _ = started_game(client)

    response = client.post(f"/api/games/{code}/turns", headers=auth(other_token))

    assert response.status_code == 401
