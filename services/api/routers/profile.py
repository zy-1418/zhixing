from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.note import Note
from models.task import Task
from models.user import User

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/{user_id}")
async def get_profile(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    note_result = await db.scalars(
        select(Note).where(Note.user_id == user_id).order_by(Note.updated_at.desc()).limit(10)
    )
    task_result = await db.scalars(
        select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc()).limit(10)
    )
    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
        "level": user.level,
        "tags": user.tags,
        "works": [
            {"id": str(note.id), "title": note.title, "template_type": note.template_type}
            for note in note_result.all()
        ],
        "recent_tasks": [
            {"id": str(task.id), "instruction": task.instruction, "status": task.status}
            for task in task_result.all()
        ],
        "likes": [],
        "collections": [],
    }
