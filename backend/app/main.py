from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.game.errors import GameError, InvalidPlayerCount
from app.rooms import GameNotFound, InvalidToken, RoomRegistry

# Domain and room errors -> HTTP status. Any other GameError is a conflict
# with the current game state (409).
ERROR_STATUS: dict[type[Exception], int] = {
    GameNotFound: status.HTTP_404_NOT_FOUND,
    InvalidToken: status.HTTP_401_UNAUTHORIZED,
    InvalidPlayerCount: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


async def handle_error(_: Request, exc: Exception) -> JSONResponse:
    code = ERROR_STATUS.get(type(exc), status.HTTP_409_CONFLICT)
    return JSONResponse(status_code=code, content={"detail": str(exc)})


def create_app() -> FastAPI:
    app = FastAPI(title="Monopoly")
    app.state.registry = RoomRegistry()

    for error in (GameError, GameNotFound, InvalidToken):
        app.add_exception_handler(error, handle_error)

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(router)
    return app


app = create_app()
