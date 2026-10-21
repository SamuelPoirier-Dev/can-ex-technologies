"""API request/response schemas and the conversion from the domain Game."""

from dataclasses import asdict
from typing import Annotated, Any

from pydantic import BaseModel, Field, StringConstraints

from app.game.board import MAX_PLAYERS, MIN_PLAYERS
from app.game.events import (
    Bankrupted,
    Event,
    GameWon,
    Moved,
    PropertyBought,
    RentPaid,
    SalaryCollected,
)
from app.game.models import Game, GameStatus

PlayerName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)
]


# --- Requests ---


class CreateGameRequest(BaseModel):
    max_players: int = Field(ge=MIN_PLAYERS, le=MAX_PLAYERS)
    player_name: PlayerName


class JoinGameRequest(BaseModel):
    player_name: PlayerName


# --- Game state (shared by REST responses and, later, WebSocket messages) ---


class SquareOut(BaseModel):
    index: int
    name: str
    price: int | None
    rent: int | None
    owner_id: str | None


class PlayerOut(BaseModel):
    id: str
    name: str
    money: int
    position: int
    is_bankrupt: bool
    properties: list[int]


class GameOut(BaseModel):
    id: str
    status: GameStatus
    max_players: int
    players: list[PlayerOut]
    board: list[SquareOut]
    current_player_id: str | None
    winner_id: str | None
    # Each event is its domain fields plus a "type" tag, e.g. {"type": "moved", ...}.
    events: list[dict[str, Any]]


# --- Responses ---


class JoinResponse(BaseModel):
    player_id: str
    token: str
    game: GameOut


class TurnResponse(BaseModel):
    events: list[dict[str, Any]]
    game: GameOut


# --- Conversion ---

EVENT_TYPES: dict[type, str] = {
    Moved: "moved",
    SalaryCollected: "salary_collected",
    PropertyBought: "property_bought",
    RentPaid: "rent_paid",
    Bankrupted: "bankrupted",
    GameWon: "game_won",
}


def serialize_event(event: Event) -> dict[str, Any]:
    return {"type": EVENT_TYPES[type(event)], **asdict(event)}


def game_state(game: Game) -> GameOut:
    return GameOut(
        id=game.id,
        status=game.status,
        max_players=game.max_players,
        players=[
            PlayerOut(
                id=p.id,
                name=p.name,
                money=p.money,
                position=p.position,
                is_bankrupt=p.is_bankrupt,
                properties=game.properties_of(p.id),
            )
            for p in game.players
        ],
        board=[
            SquareOut(
                index=i,
                name=s.name,
                price=s.price,
                rent=s.rent,
                owner_id=game.owners.get(i),
            )
            for i, s in enumerate(game.board.squares)
        ],
        current_player_id=(
            game.current_player.id if game.status is GameStatus.IN_PROGRESS else None
        ),
        winner_id=game.winner_id,
        events=[serialize_event(e) for e in game.events],
    )
