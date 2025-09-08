from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TagCategory(str, Enum):  # type: ignore[misc]
    general = "general"
    development = "development"
    nutrition = "nutrition"
    medical = "medical"
    other = "other"


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[Optional[TagCategory]] = mapped_column(
        Enum(TagCategory, name="tag_category")
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ChildTag(Base):
    __tablename__ = "child_tag"
    __table_args__ = (
        UniqueConstraint("child_id", "tag_id", name="uq_child_tag_pair"),
    )

    child_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("child_profile.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True
    )

