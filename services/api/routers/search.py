from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import String, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.note import Note

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/index")
async def rebuild_index():
    return {
        "status": "placeholder",
        "engine": "meilisearch",
        "detail": "Meilisearch is unavailable in Cloud; notes are searched via PostgreSQL fallback.",
    }


@router.get("")
async def search(
    q: str = Query(..., min_length=1),
    user_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    pattern = f"%{q}%"
    stmt = select(Note)
    if user_id is not None:
        stmt = stmt.where(Note.user_id == user_id)
    stmt = stmt.where(or_(Note.title.ilike(pattern), Note.blocks.cast(String).ilike(pattern)))
    result = await db.scalars(stmt.limit(20))
    notes = [
        {
            "type": "note",
            "id": str(note.id),
            "title": note.title,
            "template_type": note.template_type,
            "updated_at": note.updated_at.isoformat(),
        }
        for note in result.all()
    ]
    return {"query": q, "engine": "postgres-fallback", "results": notes}
