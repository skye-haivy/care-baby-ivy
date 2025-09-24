from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class TagOut(BaseModel):
    slug: str
    label: str
    category: Optional[str] = None


class ChildTagsOut(BaseModel):
    child_id: str
    tags: list[TagOut]
    suggestions: Optional[list[TagOut]] = None


class ChildTagsIn(BaseModel):
    tags: list[str]

