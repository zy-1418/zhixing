from __future__ import annotations

import uuid
from typing import Any

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from models.note import Note

router = APIRouter(prefix="/dify", tags=["dify"])


class DifyChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    user: str = Field(..., min_length=1)
    conversation_id: str | None = None
    response_mode: str = "blocking"
    inputs: dict[str, Any] = Field(default_factory=dict)
    note_ids: list[uuid.UUID] = Field(default_factory=list)


def _require_dify() -> None:
    if not settings.dify_api_key:
        raise HTTPException(
            status_code=503,
            detail="Dify is not configured. Set DIFY_API_KEY and DIFY_API_URL.",
        )


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.dify_api_key}"}


async def _load_note_context(note_ids: list[uuid.UUID], db: AsyncSession) -> str:
    if not note_ids:
        return ""
    result = await db.scalars(select(Note).where(Note.id.in_(note_ids)))
    chunks: list[str] = []
    for note in result.all():
        chunks.append(f"## {note.title or '未命名笔记'}\n{note.blocks}")
    return "\n\n".join(chunks)


@router.post("/chat")
async def proxy_chat(body: DifyChatRequest, db: AsyncSession = Depends(get_db)):
    _require_dify()
    note_context = await _load_note_context(body.note_ids, db)
    inputs = dict(body.inputs)
    if note_context:
        inputs["zhixing_note_context"] = note_context

    payload = {
        "query": body.query,
        "inputs": inputs,
        "response_mode": body.response_mode,
        "user": body.user,
    }
    if body.conversation_id:
        payload["conversation_id"] = body.conversation_id

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.dify_api_url.rstrip('/')}/chat-messages",
            headers=_headers(),
            json=payload,
        )
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@router.post("/upload")
async def proxy_upload(user: str, file: UploadFile = File(...)):
    _require_dify()
    content = await file.read()
    files = {"file": (file.filename, content, file.content_type or "application/octet-stream")}
    data = {"user": user}
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.dify_api_url.rstrip('/')}/files/upload",
            headers=_headers(),
            files=files,
            data=data,
        )
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()
