from __future__ import annotations

import logging
import time

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.v1.children import router as children_router
from app.api.v1.tags import router as tags_router
from app.core.config import settings

logger = logging.getLogger("care_baby_ivy")

app = FastAPI(title="Care Baby Ivy")


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    request.state.process_time_ms = duration_ms
    if request.url.path.startswith("/api/v1/tags/suggest"):
        logger.info(
            "tags.suggest duration=%.2fms query=%s limit=%s",
            duration_ms,
            request.query_params.get("q"),
            request.query_params.get("limit"),
        )
    response.headers.setdefault("X-Process-Time-Ms", f"{duration_ms:.2f}")
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"service": app.title, "env": settings.environment}


app.include_router(tags_router)
app.include_router(children_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    logger.warning(
        "HTTPException status=%s detail=%s path=%s",
        exc.status_code,
        detail,
        request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error path=%s errors=%s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "invalid_request", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error path=%s", request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "server_error"},
    )
