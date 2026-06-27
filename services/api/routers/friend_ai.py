from __future__ import annotations

import uuid

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from config import settings

router = APIRouter(prefix="/friend-ai", tags=["friend-ai"])


class FriendAISwitchRequest(BaseModel):
    viewer_user_id: uuid.UUID
    friend_user_id: uuid.UUID


def _collection_name(user_id: uuid.UUID) -> str:
    return f"zhixing_user_{str(user_id).replace('-', '_')}_notes"


def _headers() -> dict[str, str]:
    if not settings.qdrant_api_key:
        return {}
    return {"api-key": settings.qdrant_api_key}


@router.post("/switch")
async def switch_friend_ai(body: FriendAISwitchRequest):
    collection = _collection_name(body.friend_user_id)
    return {
        "mode": "friend-ai",
        "viewer_user_id": str(body.viewer_user_id),
        "friend_user_id": str(body.friend_user_id),
        "qdrant_collection": collection,
        "dify_inputs": {
            "friend_user_id": str(body.friend_user_id),
            "collection": collection,
        },
    }


@router.post("/{user_id}/reindex")
async def reindex_friend_ai(user_id: uuid.UUID):
    collection = _collection_name(user_id)
    url = f"{settings.qdrant_url.rstrip('/')}/collections/{collection}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.put(
                url,
                headers=_headers(),
                json={"vectors": {"size": 1536, "distance": "Cosine"}},
            )
        response.raise_for_status()
        return {"mode": "qdrant", "collection": collection, "result": response.json()}
    except Exception as exc:
        return {
            "mode": "placeholder",
            "status": "skipped",
            "collection": collection,
            "reason": f"Qdrant unavailable: {exc}",
        }
