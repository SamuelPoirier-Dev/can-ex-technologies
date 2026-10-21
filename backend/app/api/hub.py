"""LiveHub: tracks the WebSocket connections watching each game and pushes state."""

from collections import defaultdict

from fastapi import WebSocket

from app.api.schemas import GameOut


def state_message(game: GameOut) -> dict:
    return {"type": "state", "game": game.model_dump(mode="json")}


class LiveHub:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    def connection_count(self, code: str) -> int:
        return len(self._connections.get(code, ()))

    def add(self, code: str, websocket: WebSocket) -> None:
        self._connections[code].add(websocket)

    def remove(self, code: str, websocket: WebSocket) -> None:
        connections = self._connections.get(code)
        if connections is None:
            return
        connections.discard(websocket)
        if not connections:
            del self._connections[code]

    async def broadcast(self, code: str, game: GameOut) -> None:
        message = state_message(game)
        for websocket in list(self._connections.get(code, ())):
            try:
                await websocket.send_json(message)
            except Exception:
                # A closed tab must not fail the request of the player who acted.
                self.remove(code, websocket)
