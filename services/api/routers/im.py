from __future__ import annotations

import uuid
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from config import settings

router = APIRouter(prefix="/im", tags=["im"])


class IMTokenRequest(BaseModel):
    user_id: uuid.UUID
    nickname: str = Field(..., min_length=1, max_length=128)
    face_url: str | None = None


def _placeholder(kind: str) -> dict[str, Any]:
    return {
        "mode": "placeholder",
        "provider": "openim",
        "kind": kind,
        "status": "skipped",
        "reason": "OPENIM_ADMIN_TOKEN is not configured in this environment.",
    }


@router.get("/health")
async def openim_health():
    if not settings.openim_admin_token:
        return _placeholder("health")

    url = f"{settings.openim_api_base_url.rstrip('/')}/health"
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url)
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@router.post("/users/token")
async def issue_user_token(body: IMTokenRequest):
    if not settings.openim_admin_token:
        result = _placeholder("users/token")
        result["user_id"] = str(body.user_id)
        result["nickname"] = body.nickname
        return result

    url = f"{settings.openim_api_base_url.rstrip('/')}/user/token"
    headers = {"token": settings.openim_admin_token}
    payload = {
        "userID": str(body.user_id),
        "nickname": body.nickname,
        "faceURL": body.face_url or "",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, headers=headers, json=payload)
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()
