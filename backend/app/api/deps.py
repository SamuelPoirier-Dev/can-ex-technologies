"""Shared FastAPI dependencies. Tests override them via `dependency_overrides`."""

import random
from collections.abc import Callable

from fastapi import Depends
from fastapi.requests import HTTPConnection
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.hub import LiveHub
from app.game.board import DICE_SIDES
from app.rooms import RoomRegistry

DiceRoller = Callable[[], int]

bearer = HTTPBearer(auto_error=False)


# HTTPConnection works for both HTTP requests and WebSockets.
def get_registry(connection: HTTPConnection) -> RoomRegistry:
    return connection.app.state.registry


def get_hub(connection: HTTPConnection) -> LiveHub:
    return connection.app.state.hub


def get_dice() -> DiceRoller:
    return lambda: random.randint(1, DICE_SIDES)


def get_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> str | None:
    return credentials.credentials if credentials else None
