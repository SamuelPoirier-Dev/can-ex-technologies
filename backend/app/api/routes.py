"""HTTP routes. Thin layer: parse input, call the room/game, serialize output.

Routes are `async` and never await while mutating a game, so on a single
process two requests cannot interleave on the same game (no lock needed).
The game is fully updated before the live broadcast awaits.
"""

from fastapi import APIRouter, Depends, status

from app.api.deps import DiceRoller, get_dice, get_hub, get_registry, get_token
from app.api.hub import LiveHub
from app.api.schemas import (
    CreateGameRequest,
    GameOut,
    JoinGameRequest,
    JoinResponse,
    TurnResponse,
    game_state,
    serialize_event,
)
from app.rooms import RoomRegistry

router = APIRouter(prefix="/api/games", tags=["games"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_game(
    body: CreateGameRequest, registry: RoomRegistry = Depends(get_registry)
) -> JoinResponse:
    # Nobody can be watching a game that did not exist yet: no broadcast.
    room = registry.create(body.max_players)
    player, token = room.join(body.player_name)
    return JoinResponse(player_id=player.id, token=token, game=game_state(room.game))


@router.post("/{code}/players", status_code=status.HTTP_201_CREATED)
async def join_game(
    code: str,
    body: JoinGameRequest,
    registry: RoomRegistry = Depends(get_registry),
    hub: LiveHub = Depends(get_hub),
) -> JoinResponse:
    room = registry.get(code)
    player, token = room.join(body.player_name)
    state = game_state(room.game)
    await hub.broadcast(room.game.id, state)
    return JoinResponse(player_id=player.id, token=token, game=state)


@router.get("/{code}")
async def get_game(code: str, registry: RoomRegistry = Depends(get_registry)) -> GameOut:
    return game_state(registry.get(code).game)


@router.post("/{code}/turns")
async def play_turn(
    code: str,
    registry: RoomRegistry = Depends(get_registry),
    hub: LiveHub = Depends(get_hub),
    token: str | None = Depends(get_token),
    roll_dice: DiceRoller = Depends(get_dice),
) -> TurnResponse:
    room = registry.get(code)
    player_id = room.player_id_for(token)
    events = room.game.play_turn(player_id, roll_dice())
    state = game_state(room.game)
    await hub.broadcast(room.game.id, state)
    return TurnResponse(events=[serialize_event(e) for e in events], game=state)
