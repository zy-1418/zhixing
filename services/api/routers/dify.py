from __future__ import annotations

import uuid
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from models.note import Note

router = APIRouter(prefix="/dify", tags=["dify"])


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    conversation_id: str | None = None
    note_ids: list[uuid.UUID] = Field(default_factory=list)
    inputs: dict[str, Any] = Field(default_factory=dict)
    user: str | None = None


async def _note_context(note_ids: list[uuid.UUID], db: AsyncSession) -> str:
    if not note_ids:
        return ""
    rows = await db.scalars(select(Note).where(Note.id.in_(note_ids)))
    sections = []
    for note in rows.all():
        sections.append(f"## {note.title}\n{note.blocks}")
    return "\n\n".join(sections)


@router.post("/chat")
async def chat(body: ChatRequest, db: AsyncSession = Depends(get_db)):
    context = await _note_context(body.note_ids, db)
    query = body.query if not context else f"{body.query}\n\n@引用笔记:\n{context}"
    payload = {
        "inputs": body.inputs,
        "query": query,
        "response_mode": "blocking",
        "conversation_id": body.conversation_id,
        "user": body.user or settings.dify_user,
    }

    if not settings.dify_api_key:
        return {
            "blocked": True,
            "reason": "DIFY_API_KEY is not configured",
            "echo": payload,
        }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{settings.dify_api_url.rstrip('/')}/v1/chat-messages",
                headers={"Authorization": f"Bearer {settings.dify_api_key}"},
                json=payload,
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Dify proxy failed: {exc}") from exc


@router.post("/upload")
async def upload(request: Request):
    if not settings.dify_api_key:
        return {
            "blocked": True,
            "reason": "DIFY_API_KEY is not configured",
            "filename": request.headers.get("x-filename"),
        }
    data = await request.body()
    content_type = request.headers.get("content-type", "application/octet-stream")
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{settings.dify_api_url.rstrip('/')}/v1/files/upload",
                headers={
                    "Authorization": f"Bearer {settings.dify_api_key}",
                    "Content-Type": content_type,
                },
                content=data,
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Dify upload failed: {exc}") from exc
