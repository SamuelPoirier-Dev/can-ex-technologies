"""In-memory game rooms: a domain Game plus the access tokens of its players.

The domain knows nothing about tokens or networking; rooms add that layer.
"""

import secrets
from dataclasses import dataclass, field

from app.game.models import Game, Player

# No 0/O or 1/I, so codes are easy to read aloud and type.
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
CODE_LENGTH = 6


class GameNotFound(Exception):
    pass


class InvalidToken(Exception):
    pass


@dataclass
class GameRoom:
    game: Game
    # Token -> player id. Tokens are secrets and never leave this object
    # except once, in the response to the player who joined.
    tokens: dict[str, str] = field(default_factory=dict)

    def join(self, name: str) -> tuple[Player, str]:
        player = self.game.add_player(name)
        token = secrets.token_urlsafe(16)
        self.tokens[token] = player.id
        return player, token

    def player_id_for(self, token: str | None) -> str:
        if token is None or token not in self.tokens:
            raise InvalidToken("Missing or invalid player token")
        return self.tokens[token]


class RoomRegistry:
    def __init__(self) -> None:
        self._rooms: dict[str, GameRoom] = {}

    def create(self, max_players: int) -> GameRoom:
        code = self._new_code()
        room = GameRoom(game=Game(id=code, max_players=max_players))
        self._rooms[code] = room
        return room

    def get(self, code: str) -> GameRoom:
        room = self._rooms.get(code.upper())
        if room is None:
            raise GameNotFound(f"No game with code {code}")
        return room

    def _new_code(self) -> str:
        while True:
            code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
            if code not in self._rooms:
                return code
