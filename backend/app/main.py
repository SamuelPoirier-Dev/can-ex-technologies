from fastapi import FastAPI

app = FastAPI(title="Monopoly")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
