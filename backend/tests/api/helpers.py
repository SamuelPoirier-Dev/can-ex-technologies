"""Helpers shared by the API tests."""

from fastapi.testclient import TestClient

FIXED_ROLL = 1  # Lands on square 1, a property.


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
