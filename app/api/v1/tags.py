from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.db import get_db
from app.models.child import ChildProfile
from app.models.tag import ChildTag, Tag
from app.schemas.tags import ChildTagsIn, ChildTagsOut, TagOut
from app.services import tagging as tagging_service


router = APIRouter(prefix="/api/v1")


def get_current_user_id(request: Request) -> str:
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    return user_id


def assert_child_owned(db: Session, child_id: str, user_id: str) -> ChildProfile:
    try:
        cid = uuid.UUID(str(child_id))
    except Exception:
        # child_id path param invalid
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")

    child = db.get(ChildProfile, cid)
    if child is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")

    if str(child.user_id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

    return child


@router.get("/children/{child_id}/tags", response_model=ChildTagsOut)
def get_child_tags(
    child_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> ChildTagsOut:
    assert_child_owned(db, child_id, user_id)

    # Fetch current tags
    rows = (
        db.execute(
            select(Tag).join(ChildTag, ChildTag.tag_id == Tag.id).where(ChildTag.child_id == uuid.UUID(child_id))
        )
        .scalars()
        .all()
    )
    tags = [TagOut(slug=t.slug, label=t.label, category=None) for t in rows]
    return ChildTagsOut(child_id=str(child_id), tags=tags, suggestions=[])


@router.put("/children/{child_id}/tags", response_model=ChildTagsOut)
def put_child_tags(
    child_id: str,
    body: ChildTagsIn,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> ChildTagsOut:
    assert_child_owned(db, child_id, user_id)

    normalized = tagging_service.child_set_tags(db, child_id, body.tags)
    tags = [TagOut(**t) for t in normalized]
    return ChildTagsOut(child_id=str(child_id), tags=tags, suggestions=[])


@router.get("/tags/suggest")
def suggest(
    q: str = Query(...),
    limit: int = Query(8, ge=1),
    db: Session = Depends(get_db),
):
    try:
        results = tagging_service.suggest_from_text(db, q, limit)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid query")
    return {"query": q, "results": results}
