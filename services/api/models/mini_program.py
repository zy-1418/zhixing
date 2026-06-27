from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MiniProgram(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "mini_programs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(128))
    prompt: Mapped[str] = mapped_column(Text)
    dify_workflow_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    ui_schema: Mapped[dict] = mapped_column(JSONB, default=dict)
