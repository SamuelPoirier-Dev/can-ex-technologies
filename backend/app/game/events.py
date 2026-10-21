"""Facts produced by a turn. They feed the live game log."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Moved:
    player_id: str
    roll: int
    from_position: int
    to_position: int


@dataclass(frozen=True)
class SalaryCollected:
    player_id: str
    amount: int


@dataclass(frozen=True)
class PropertyBought:
    player_id: str
    position: int
    price: int


@dataclass(frozen=True)
class RentPaid:
    payer_id: str
    owner_id: str
    position: int
    amount: int


@dataclass(frozen=True)
class Bankrupted:
    player_id: str
    creditor_id: str


@dataclass(frozen=True)
class GameWon:
    player_id: str


Event = Moved | SalaryCollected | PropertyBought | RentPaid | Bankrupted | GameWon
