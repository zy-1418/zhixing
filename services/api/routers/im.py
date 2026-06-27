from __future__ import annotations

import uuid

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/im", tags=["im"])


class IMTokenRequest(BaseModel):
    user_id: uuid.UUID
    nickname: str = Field(..., min_length=1, max_length=64)


@router.get("/status")
async def im_status():
    return {
        "provider": "OpenIM",
        "status": "placeholder",
        "detail": "OpenIM server is documented but not reachable in Cloud.",
    }


@router.post("/tokens")
async def issue_im_token(body: IMTokenRequest):
    return {
        "user_id": str(body.user_id),
        "nickname": body.nickname,
        "token": "openim-placeholder-token",
        "expires_in": 0,
    }
