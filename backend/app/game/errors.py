"""Domain errors raised when an action breaks the game rules."""


class GameError(Exception):
    """Base class for every rule violation."""


class InvalidPlayerCount(GameError):
    pass


class GameFull(GameError):
    pass


class GameAlreadyStarted(GameError):
    pass


class GameNotInProgress(GameError):
    pass


class NotYourTurn(GameError):
    pass


class InvalidRoll(GameError):
    pass
