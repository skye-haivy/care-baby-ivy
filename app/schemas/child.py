from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel


class ChildCreateIn(BaseModel):
    name: str
    dob: Optional[date] = None
    gender: Optional[str] = None
    region: Optional[str] = None
    language_pref: Optional[str] = None


class ChildOut(BaseModel):
    id: str
    name: str
    dob: Optional[date] = None
    gender: Optional[str] = None
    region: Optional[str] = None
    language_pref: Optional[str] = None

