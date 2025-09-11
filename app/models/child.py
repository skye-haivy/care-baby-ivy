from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

import enum
from sqlalchemy import String
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.models.base import Base, TimestampMixin


class Gender(str, enum.Enum):  # type: ignore[misc]
    female = "female"
    male = "male"
    other = "other"
    undisclosed = "undisclosed"


class ChildProfile(TimestampMixin, Base):
    __tablename__ = "child_profile"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    dob: Mapped[Optional[date]]
    gender: Mapped[Optional[Gender]] = mapped_column(sa.Enum(Gender, name="gender"))
    region: Mapped[Optional[str]] = mapped_column(String(120))
    language_pref: Mapped[Optional[str]] = mapped_column(String(50))
    age_stage: Mapped[Optional[str]] = mapped_column(String(50))

    @validates("user_id")
    def _coerce_user_id(self, key, value):  # type: ignore[override]
        try:
            if isinstance(value, uuid.UUID):
                return value
            return uuid.UUID(str(value))
        except Exception:
            # Deterministic UUID from provided string
            return uuid.uuid5(uuid.NAMESPACE_URL, f"user:{value}")

    @validates("gender")
    def _coerce_gender(self, key, value):  # type: ignore[override]
        if value is None:
            return None
        if isinstance(value, Gender):
            return value
        s = str(value).lower().strip()
        mapping = {"f": Gender.female, "m": Gender.male, "female": Gender.female, "male": Gender.male, "other": Gender.other, "undisclosed": Gender.undisclosed}
        return mapping.get(s, None)
