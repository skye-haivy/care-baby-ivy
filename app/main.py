from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title="Care Baby Ivy")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"service": app.title, "env": settings.environment}

