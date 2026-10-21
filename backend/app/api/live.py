"""WebSocket route: every browser watching a game gets its full state on change.

The WebSocket is receive-only for clients; actions go through REST.
"""

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.api.deps import get_hub, get_registry
from app.api.hub import LiveHub, state_message
from app.api.schemas import game_state
from app.rooms import GameNotFound, RoomRegistry

# Application-level close code, modeled on HTTP 404.
CLOSE_GAME_NOT_FOUND = 4404

router = APIRouter()


@router.websocket("/ws/games/{code}")
async def game_updates(
    websocket: WebSocket,
    code: str,
    registry: RoomRegistry = Depends(get_registry),
    hub: LiveHub = Depends(get_hub),
) -> None:
    await websocket.accept()
    try:
        room = registry.get(code)
    except GameNotFound:
        await websocket.close(code=CLOSE_GAME_NOT_FOUND)
        return

    code = room.game.id  # Normalized (upper case) code.
    hub.add(code, websocket)
    try:
        await websocket.send_json(state_message(game_state(room.game)))
        # Keep the connection open until the client leaves; incoming messages are ignored.
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        hub.remove(code, websocket)
