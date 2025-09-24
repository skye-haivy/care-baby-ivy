from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.tags import router as tags_router
from app.api.v1.children import router as children_router

app = FastAPI(title="Care Baby Ivy")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"service": app.title, "env": settings.environment}


app.include_router(tags_router)
app.include_router(children_router)
