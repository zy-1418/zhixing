from __future__ import annotations

import base64
import binascii
import uuid
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from models.note import Note

router = APIRouter(prefix="/dify", tags=["dify"])


class DifyChatRequest(BaseModel):
    user_id: uuid.UUID
    query: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None
    note_ids: list[uuid.UUID] = Field(default_factory=list)
    inputs: dict[str, Any] = Field(default_factory=dict)
    response_mode: str = "blocking"


class DifyUploadRequest(BaseModel):
    user_id: uuid.UUID
    filename: str = Field(..., min_length=1)
    content_base64: str = Field(..., min_length=1)
    mime_type: str = "application/octet-stream"


def _headers() -> dict[str, str]:
    if not settings.dify_api_key:
        return {}
    return {"Authorization": f"Bearer {settings.dify_api_key}"}


def _dify_unconfigured_response(kind: str) -> dict[str, Any]:
    return {
        "mode": "placeholder",
        "provider": "dify",
        "status": "skipped",
        "reason": "DIFY_API_KEY is not configured in this environment.",
        "kind": kind,
    }


async def _note_context(note_ids: list[uuid.UUID], db: AsyncSession) -> str:
    snippets: list[str] = []
    for note_id in note_ids:
        note = await db.get(Note, note_id)
        if note is None:
            raise HTTPException(status_code=404, detail=f"Note not found: {note_id}")
        snippets.append(
            "\n".join(
                [
                    f"## @{note.id} {note.title or '未命名笔记'}",
                    f"template_type: {note.template_type}",
                    f"blocks: {note.blocks}",
                ]
            )
        )
    return "\n\n".join(snippets)


async def _post_dify(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    if not settings.dify_api_key:
        return _dify_unconfigured_response(path)

    url = f"{settings.dify_api_base_url.rstrip('/')}/{path.lstrip('/')}"
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=_headers(), json=payload)
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@router.post("/chat")
async def chat(body: DifyChatRequest, db: AsyncSession = Depends(get_db)):
    context = await _note_context(body.note_ids, db)
    query = body.query
    if context:
        query = f"以下是用户 @ 引用的知行笔记上下文：\n\n{context}\n\n用户问题：{body.query}"

    payload: dict[str, Any] = {
        "inputs": body.inputs,
        "query": query,
        "response_mode": body.response_mode,
        "user": str(body.user_id),
    }
    if body.conversation_id:
        payload["conversation_id"] = body.conversation_id

    result = await _post_dify("chat-messages", payload)
    if result.get("mode") == "placeholder":
        result["query"] = query
    return result


@router.post("/upload")
async def upload(body: DifyUploadRequest):
    if not settings.dify_api_key:
        result = _dify_unconfigured_response("files/upload")
        result["filename"] = body.filename
        return result

    try:
        content = base64.b64decode(body.content_base64, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise HTTPException(status_code=400, detail="Invalid base64 content") from exc

    url = f"{settings.dify_api_base_url.rstrip('/')}/files/upload"
    files = {"file": (body.filename, content, body.mime_type)}
    data = {"user": str(body.user_id)}
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=_headers(), data=data, files=files)
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()
