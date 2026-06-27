from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class WorkspaceFolder(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "workspace_folders"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspace_folders.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(256))
    folder_type: Mapped[str] = mapped_column(String(32), default="portfolio")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User"] = relationship(back_populates="folders")
    parent: Mapped["WorkspaceFolder | None"] = relationship(
        remote_side="WorkspaceFolder.id", back_populates="children"
    )
    children: Mapped[list["WorkspaceFolder"]] = relationship(back_populates="parent")
    notes: Mapped[list["Note"]] = relationship(back_populates="folder")
    tasks: Mapped[list["Task"]] = relationship(back_populates="folder")
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="folder")
