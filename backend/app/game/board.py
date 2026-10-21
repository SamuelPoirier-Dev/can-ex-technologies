"""Static board definition: squares, prices, rents and game constants."""

from dataclasses import dataclass

# Tuned so that games actually end: see tests/game/test_balance.py.
STARTING_MONEY = 500
SALARY = 100
DICE_SIDES = 6
MIN_PLAYERS = 2
MAX_PLAYERS = 4


@dataclass(frozen=True)
class Square:
    name: str
    price: int | None = None
    rent: int | None = None

    @property
    def is_property(self) -> bool:
        return self.price is not None


@dataclass(frozen=True)
class Board:
    squares: tuple[Square, ...]

    def __len__(self) -> int:
        return len(self.squares)

    def __getitem__(self, index: int) -> Square:
        return self.squares[index]


def _property(name: str, price: int) -> Square:
    # Rent equals price: high enough for bankruptcies to happen within a short game.
    return Square(name=name, price=price, rent=price)


# Square 0 is always the start ("Départ").
DEFAULT_BOARD = Board(
    squares=(
        Square("Départ"),
        _property("Rue Saint-Vallier", 60),
        _property("Rue Saint-Joseph", 80),
        Square("Parc de la Chute-Montmorency"),
        _property("3e Avenue", 100),
        _property("Avenue Cartier", 140),
        Square("Marché du Vieux-Port"),
        _property("Avenue Maguire", 180),
        _property("Rue Saint-Jean", 200),
        Square("Plaines d'Abraham"),
        _property("Rue Saint-Paul", 240),
        _property("Grande Allée", 260),
        Square("Terrasse Dufferin"),
        _property("Rue Saint-Louis", 300),
        Square("Château Frontenac"),
        _property("Rue du Petit-Champlain", 400),
    )
)
