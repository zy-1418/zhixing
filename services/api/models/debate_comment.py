from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class DebateComment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "debate_comments"

    debate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("debates.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    side: Mapped[str] = mapped_column(String(8))
    content: Mapped[str] = mapped_column(Text)
    evidence_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=0)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)

    debate: Mapped["Debate"] = relationship(back_populates="comments")
