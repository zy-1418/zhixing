from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SocialVote(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "social_votes"
    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uq_social_votes_post_user"),
    )

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("social_posts.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    vote_type: Mapped[str] = mapped_column(String(8))
    reason: Mapped[str] = mapped_column(Text)

    post: Mapped["SocialPost"] = relationship(back_populates="votes")
