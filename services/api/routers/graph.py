from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/graph", tags=["graph"])


class RelationExtractRequest(BaseModel):
    note_id: uuid.UUID
    text: str = Field(..., min_length=1)


class FriendAIRequest(BaseModel):
    friend_user_id: uuid.UUID
    query: str = Field(..., min_length=1)


@router.post("/relations/extract")
async def extract_relations(body: RelationExtractRequest):
    keywords = [token.strip("，。,. ") for token in body.text.split() if len(token) > 1][:8]
    nodes = [{"id": keyword, "label": keyword, "type": "concept"} for keyword in keywords]
    edges = [
        {"source": keywords[index], "target": keywords[index + 1], "label": "related"}
        for index in range(max(0, len(keywords) - 1))
    ]
    return {
        "note_id": str(body.note_id),
        "engine": "neo4j-placeholder",
        "nodes": nodes,
        "edges": edges,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/sigma")
async def sigma_payload():
    return {
        "nodes": [{"key": "zhixing", "attributes": {"label": "知行", "x": 0, "y": 0}}],
        "edges": [],
        "detail": "sigma.js WebView can render this payload until Neo4j is enabled.",
    }


@router.post("/friend-ai/chat")
async def friend_ai_chat(body: FriendAIRequest):
    return {
        "friend_user_id": str(body.friend_user_id),
        "answer": "好友 AI 蒸馏需要按用户 Qdrant 分库；当前为占位响应。",
        "query": body.query,
    }


@router.post("/mini-programs/generate")
async def generate_mini_program(prompt: str):
    return {
        "status": "placeholder",
        "prompt": prompt,
        "workflow": "Dify Workflow + e2b sandbox",
    }
