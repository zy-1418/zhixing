from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.note import Note

router = APIRouter(prefix="/notes", tags=["notes"])

TemplateType = Literal["document", "dual", "canvas", "mindmap"]


class NoteCreate(BaseModel):
    user_id: uuid.UUID
    title: str = Field("", max_length=512)
    template_type: TemplateType = "document"
    folder_id: Optional[uuid.UUID] = None
    blocks: list[Any] = Field(default_factory=list)


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=512)
    template_type: Optional[TemplateType] = None
    folder_id: Optional[uuid.UUID] = None
    blocks: Optional[list[Any]] = None


class NoteResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    folder_id: Optional[uuid.UUID]
    title: str
    template_type: str
    blocks: list[Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=list[NoteResponse])
async def list_notes(
    user_id: uuid.UUID = Query(...),
    folder_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Note).where(Note.user_id == user_id)
    if folder_id is not None:
        stmt = stmt.where(Note.folder_id == folder_id)
    stmt = stmt.order_by(Note.updated_at.desc())
    result = await db.scalars(stmt)
    return result.all()


@router.get("/", response_model=list[NoteResponse])
async def list_notes_with_slash(
    user_id: uuid.UUID = Query(...),
    folder_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await list_notes(user_id=user_id, folder_id=folder_id, db=db)


@router.post("", response_model=NoteResponse, status_code=201)
async def create_note(body: NoteCreate, db: AsyncSession = Depends(get_db)):
    note = Note(
        user_id=body.user_id,
        folder_id=body.folder_id,
        title=body.title,
        template_type=body.template_type,
        blocks=body.blocks,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


@router.post("/", response_model=NoteResponse, status_code=201)
async def create_note_with_slash(body: NoteCreate, db: AsyncSession = Depends(get_db)):
    return await create_note(body=body, db=db)


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    note = await db.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.get("/{note_id}/markdown")
async def export_note_markdown(note_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    note = await db.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    lines = [f"# {note.title or '未命名笔记'}", ""]
    for block in note.blocks:
        if isinstance(block, dict):
            text = block.get("text") or block.get("content") or block
        else:
            text = block
        lines.extend([str(text), ""])
    return Response("\n".join(lines), media_type="text/markdown; charset=utf-8")


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: uuid.UUID,
    body: NoteUpdate,
    db: AsyncSession = Depends(get_db),
):
    note = await db.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(note, field, value)

    await db.commit()
    await db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=204)
async def delete_note(note_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    note = await db.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    await db.delete(note)
    await db.commit()
