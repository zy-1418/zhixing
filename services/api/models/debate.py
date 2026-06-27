from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Debate(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "debates"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    topic: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text, default="")

    comments: Mapped[list["DebateComment"]] = relationship(back_populates="debate")
