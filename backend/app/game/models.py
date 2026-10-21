"""Game aggregate: owns the state of one game and enforces its rules."""

from dataclasses import dataclass, field
from enum import StrEnum

from app.game.board import (
    DEFAULT_BOARD,
    DICE_SIDES,
    MAX_PLAYERS,
    MIN_PLAYERS,
    SALARY,
    STARTING_MONEY,
    Board,
)
from app.game.errors import (
    GameAlreadyStarted,
    GameFull,
    GameNotInProgress,
    InvalidPlayerCount,
    InvalidRoll,
    NotYourTurn,
)
from app.game.events import (
    Bankrupted,
    Event,
    GameWon,
    Moved,
    PropertyBought,
    RentPaid,
    SalaryCollected,
)


class GameStatus(StrEnum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


@dataclass
class Player:
    id: str
    name: str
    money: int = STARTING_MONEY
    position: int = 0
    is_bankrupt: bool = False


@dataclass
class Game:
    id: str
    max_players: int
    board: Board = DEFAULT_BOARD
    players: list[Player] = field(default_factory=list)
    # Square index -> owner player id. The board itself stays static.
    owners: dict[int, str] = field(default_factory=dict)
    current_index: int = 0
    status: GameStatus = GameStatus.WAITING
    winner_id: str | None = None
    events: list[Event] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not MIN_PLAYERS <= self.max_players <= MAX_PLAYERS:
            raise InvalidPlayerCount(
                f"A game needs {MIN_PLAYERS} to {MAX_PLAYERS} players"
            )

    # --- Queries ---

    @property
    def current_player(self) -> Player:
        return self.players[self.current_index]

    def player(self, player_id: str) -> Player:
        return next(p for p in self.players if p.id == player_id)

    def properties_of(self, player_id: str) -> list[int]:
        return sorted(pos for pos, owner in self.owners.items() if owner == player_id)

    # --- Commands ---

    def add_player(self, name: str) -> Player:
        if self.status is not GameStatus.WAITING:
            raise GameAlreadyStarted("The game has already started")
        if len(self.players) >= self.max_players:
            raise GameFull("The game is full")

        player = Player(id=f"p{len(self.players) + 1}", name=name)
        self.players.append(player)
        if len(self.players) == self.max_players:
            self.status = GameStatus.IN_PROGRESS
        return player

    def play_turn(self, player_id: str, roll: int) -> list[Event]:
        if self.status is not GameStatus.IN_PROGRESS:
            raise GameNotInProgress("The game is not in progress")
        if self.current_player.id != player_id:
            raise NotYourTurn("It is not your turn")
        if not 1 <= roll <= DICE_SIDES:
            raise InvalidRoll(f"A roll must be between 1 and {DICE_SIDES}")

        player = self.current_player
        events = self._move(player, roll)
        events += self._resolve_square(player)
        if self.status is GameStatus.IN_PROGRESS:
            self._advance_turn()

        self.events.extend(events)
        return events

    # --- Turn steps ---

    def _move(self, player: Player, roll: int) -> list[Event]:
        start = player.position
        player.position = (start + roll) % len(self.board)
        events: list[Event] = [Moved(player.id, roll, start, player.position)]

        # Landing exactly on the start counts as passing it.
        if start + roll >= len(self.board):
            player.money += SALARY
            events.append(SalaryCollected(player.id, SALARY))
        return events

    def _resolve_square(self, player: Player) -> list[Event]:
        square = self.board[player.position]
        if not square.is_property:
            return []
        assert square.price is not None and square.rent is not None

        owner_id = self.owners.get(player.position)
        if owner_id is None:
            return self._buy(player, square.price)
        if owner_id == player.id:
            return []
        return self._pay_rent(player, self.player(owner_id), square.rent)

    def _buy(self, player: Player, price: int) -> list[Event]:
        if player.money < price:
            return []
        player.money -= price
        self.owners[player.position] = player.id
        return [PropertyBought(player.id, player.position, price)]

    def _pay_rent(self, payer: Player, owner: Player, rent: int) -> list[Event]:
        # A player who cannot pay in full hands over everything left, then goes bankrupt.
        amount = min(rent, payer.money)
        payer.money -= amount
        owner.money += amount
        events: list[Event] = [RentPaid(payer.id, owner.id, payer.position, amount)]

        if amount < rent:
            events += self._bankrupt(payer, creditor=owner)
        return events

    def _bankrupt(self, player: Player, creditor: Player) -> list[Event]:
        player.is_bankrupt = True
        # Bankrupt players' properties go back to the bank.
        self.owners = {pos: o for pos, o in self.owners.items() if o != player.id}
        events: list[Event] = [Bankrupted(player.id, creditor.id)]

        remaining = [p for p in self.players if not p.is_bankrupt]
        if len(remaining) == 1:
            self.status = GameStatus.FINISHED
            self.winner_id = remaining[0].id
            events.append(GameWon(self.winner_id))
        return events

    def _advance_turn(self) -> None:
        # Skip bankrupt players. At least two players remain while the game is in progress.
        index = self.current_index
        while True:
            index = (index + 1) % len(self.players)
            if not self.players[index].is_bankrupt:
                self.current_index = index
                return
