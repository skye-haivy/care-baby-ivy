from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.child import ChildProfile
from app.schemas.child import ChildCreateIn, ChildOut


router = APIRouter(prefix="/api/v1")


def get_current_user_id(request: Request) -> str:
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    return user_id


@router.post("/children", response_model=ChildOut)
def create_child(
    body: ChildCreateIn,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> ChildOut:
    c = ChildProfile(
        user_id=user_id,
        name=body.name,
        dob=body.dob,
        gender=body.gender,
        region=body.region,
        language_pref=body.language_pref,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return ChildOut(
        id=str(c.id),
        name=c.name,
        dob=c.dob,
        gender=c.gender.value if c.gender is not None else None,
        region=c.region,
        language_pref=c.language_pref,
    )

