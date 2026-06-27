from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Task(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "tasks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    folder_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspace_folders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    instruction: Mapped[str] = mapped_column(Text)
    name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    workflow_type: Mapped[str] = mapped_column(String(32), default="custom")
    priority: Mapped[str] = mapped_column(String(16), default="medium")
    status: Mapped[str] = mapped_column(String(32), default="pending")
    metagpt_job_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    user: Mapped["User"] = relationship(back_populates="tasks")
    folder: Mapped["WorkspaceFolder | None"] = relationship(back_populates="tasks")
