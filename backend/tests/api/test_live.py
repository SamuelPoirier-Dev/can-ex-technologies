import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.api.live import CLOSE_GAME_NOT_FOUND
from tests.api.helpers import auth, create_game, join_game, started_game


def test_receives_current_state_on_connect(client: TestClient) -> None:
    code = create_game(client)["game"]["id"]

    with client.websocket_connect(f"/ws/games/{code}") as ws:
        message = ws.receive_json()

    assert message["type"] == "state"
    assert message["game"]["id"] == code
    assert message["game"]["status"] == "waiting"


def test_code_is_case_insensitive(client: TestClient) -> None:
    code = create_game(client)["game"]["id"]

    with client.websocket_connect(f"/ws/games/{code.lower()}") as ws:
        assert ws.receive_json()["game"]["id"] == code


def test_receives_state_when_a_player_joins(client: TestClient) -> None:
    code = create_game(client)["game"]["id"]

    with client.websocket_connect(f"/ws/games/{code}") as ws:
        ws.receive_json()  # Initial state.
        join_game(client, code, name="Bob")
        message = ws.receive_json()

    assert [p["name"] for p in message["game"]["players"]] == ["Alice", "Bob"]
    assert message["game"]["status"] == "in_progress"


def test_every_watcher_receives_the_turn(client: TestClient) -> None:
    code, alice_token, _ = started_game(client)

    with (
        client.websocket_connect(f"/ws/games/{code}") as alice_ws,
        client.websocket_connect(f"/ws/games/{code}") as bob_ws,
    ):
        alice_ws.receive_json()
        bob_ws.receive_json()
        response = client.post(f"/api/games/{code}/turns", headers=auth(alice_token))
        received = [alice_ws.receive_json(), bob_ws.receive_json()]

    for message in received:
        assert message == {"type": "state", "game": response.json()["game"]}


def test_unknown_game_closes_connection(client: TestClient) -> None:
    with client.websocket_connect("/ws/games/NOPE42") as ws:
        with pytest.raises(WebSocketDisconnect) as closed:
            ws.receive_json()

    assert closed.value.code == CLOSE_GAME_NOT_FOUND


def test_connection_is_released_when_client_leaves(client: TestClient) -> None:
    code = create_game(client)["game"]["id"]
    hub = client.app.state.hub  # type: ignore[attr-defined]

    with client.websocket_connect(f"/ws/games/{code}") as ws:
        ws.receive_json()
        assert hub.connection_count(code) == 1

    # Leaving the block closes the socket and waits for the server handler to finish.
    assert hub.connection_count(code) == 0
