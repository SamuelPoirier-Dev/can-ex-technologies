"""HTTP routes. Thin layer: parse input, call the room/game, serialize output.

Routes are `async` and never await while mutating a game, so on a single
process two requests cannot interleave on the same game (no lock needed).
"""

import random
from collections.abc import Callable

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.schemas import (
    CreateGameRequest,
    GameOut,
    JoinGameRequest,
    JoinResponse,
    TurnResponse,
    game_state,
    serialize_event,
)
from app.game.board import DICE_SIDES
from app.rooms import RoomRegistry

router = APIRouter(prefix="/api/games", tags=["games"])
bearer = HTTPBearer(auto_error=False)

DiceRoller = Callable[[], int]


def get_registry(request: Request) -> RoomRegistry:
    return request.app.state.registry


def get_dice() -> DiceRoller:
    return lambda: random.randint(1, DICE_SIDES)


def get_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> str | None:
    return credentials.credentials if credentials else None


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_game(
    body: CreateGameRequest, registry: RoomRegistry = Depends(get_registry)
) -> JoinResponse:
    room = registry.create(body.max_players)
    player, token = room.join(body.player_name)
    return JoinResponse(player_id=player.id, token=token, game=game_state(room.game))


@router.post("/{code}/players", status_code=status.HTTP_201_CREATED)
async def join_game(
    code: str, body: JoinGameRequest, registry: RoomRegistry = Depends(get_registry)
) -> JoinResponse:
    room = registry.get(code)
    player, token = room.join(body.player_name)
    return JoinResponse(player_id=player.id, token=token, game=game_state(room.game))


@router.get("/{code}")
async def get_game(code: str, registry: RoomRegistry = Depends(get_registry)) -> GameOut:
    return game_state(registry.get(code).game)


@router.post("/{code}/turns")
async def play_turn(
    code: str,
    registry: RoomRegistry = Depends(get_registry),
    token: str | None = Depends(get_token),
    roll_dice: DiceRoller = Depends(get_dice),
) -> TurnResponse:
    room = registry.get(code)
    player_id = room.player_id_for(token)
    events = room.game.play_turn(player_id, roll_dice())
    return TurnResponse(
        events=[serialize_event(e) for e in events], game=game_state(room.game)
    )
