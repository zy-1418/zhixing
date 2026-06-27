from __future__ import annotations

import uuid
from typing import Any, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from config import settings

router = APIRouter(prefix="/dify", tags=["dify"])


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    user: str = Field("anonymous", min_length=1)
    conversation_id: Optional[str] = None
    note_ids: list[uuid.UUID] = Field(default_factory=list)
    inputs: dict[str, Any] = Field(default_factory=dict)


class UploadPlaceholderRequest(BaseModel):
    filename: str
    content_type: str = "application/octet-stream"
    note_ids: list[uuid.UUID] = Field(default_factory=list)


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.dify_api_key}",
        "Content-Type": "application/json",
    }


@router.post("/chat-messages")
async def chat_messages(body: ChatRequest):
    if not settings.dify_api_key:
        return {
            "mode": "placeholder",
            "answer": "Dify API Key 未配置；当前返回本地占位回答。",
            "conversation_id": body.conversation_id or f"local-{uuid.uuid4().hex[:8]}",
            "referenced_note_ids": [str(note_id) for note_id in body.note_ids],
        }

    payload = {
        "query": body.query,
        "inputs": {
            **body.inputs,
            "referenced_note_ids": [str(note_id) for note_id in body.note_ids],
        },
        "response_mode": "blocking",
        "user": body.user,
    }
    if body.conversation_id:
        payload["conversation_id"] = body.conversation_id

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.dify_api_base.rstrip('/')}/chat-messages",
            headers=_headers(),
            json=payload,
        )
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@router.post("/files/upload")
async def upload_placeholder(body: UploadPlaceholderRequest):
    if not settings.dify_api_key:
        return {
            "mode": "placeholder",
            "file_id": f"local-file-{uuid.uuid4().hex[:8]}",
            "filename": body.filename,
            "content_type": body.content_type,
            "referenced_note_ids": [str(note_id) for note_id in body.note_ids],
        }
    raise HTTPException(
        status_code=501,
        detail="Binary multipart upload is documented for the mobile client but not enabled in Cloud.",
    )


@router.get("/agent/lin")
async def lin_agent_status():
    return {
        "name": "林",
        "provider": "Dify",
        "configured": bool(settings.dify_api_key),
        "api_base": settings.dify_api_base,
        "capabilities": ["chat", "rag", "@note-reference", "tool-market-sync"],
    }
