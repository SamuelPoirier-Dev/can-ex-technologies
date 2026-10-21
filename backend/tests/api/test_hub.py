import asyncio
from typing import Any

from app.api.hub import LiveHub
from app.api.schemas import game_state
from app.game.models import Game


class FakeWebSocket:
    def __init__(self, broken: bool = False) -> None:
        self.broken = broken
        self.sent: list[Any] = []

    async def send_json(self, data: Any) -> None:
        if self.broken:
            raise RuntimeError("connection closed")
        self.sent.append(data)


def broadcast(hub: LiveHub, code: str, game: Game) -> None:
    asyncio.run(hub.broadcast(code, game_state(game)))


def test_broadcast_reaches_only_watchers_of_that_game() -> None:
    hub = LiveHub()
    watcher, other = FakeWebSocket(), FakeWebSocket()
    hub.add("AAAAAA", watcher)  # type: ignore[arg-type]
    hub.add("BBBBBB", other)  # type: ignore[arg-type]

    broadcast(hub, "AAAAAA", Game(id="AAAAAA", max_players=2))

    assert len(watcher.sent) == 1
    assert watcher.sent[0]["type"] == "state"
    assert other.sent == []


def test_broken_connection_is_dropped_without_affecting_others() -> None:
    hub = LiveHub()
    healthy, broken = FakeWebSocket(), FakeWebSocket(broken=True)
    hub.add("AAAAAA", healthy)  # type: ignore[arg-type]
    hub.add("AAAAAA", broken)  # type: ignore[arg-type]

    broadcast(hub, "AAAAAA", Game(id="AAAAAA", max_players=2))

    assert len(healthy.sent) == 1
    assert hub.connection_count("AAAAAA") == 1


def test_removing_last_connection_forgets_the_game() -> None:
    hub = LiveHub()
    ws = FakeWebSocket()
    hub.add("AAAAAA", ws)  # type: ignore[arg-type]

    hub.remove("AAAAAA", ws)  # type: ignore[arg-type]
    hub.remove("AAAAAA", ws)  # type: ignore[arg-type]  # Idempotent.

    assert hub.connection_count("AAAAAA") == 0
