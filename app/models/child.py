from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Gender(str, Enum):  # type: ignore[misc]
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
    gender: Mapped[Optional[Gender]] = mapped_column(Enum(Gender, name="gender"))
    region: Mapped[Optional[str]] = mapped_column(String(120))
    language_pref: Mapped[Optional[str]] = mapped_column(String(50))
    age_stage: Mapped[Optional[str]] = mapped_column(String(50))

