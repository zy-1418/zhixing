from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(tags=["social"])

VoteValue = Literal["up", "down"]

_posts: dict[str, dict] = {}
_debates: dict[str, dict] = {}
_market_agents: list[dict] = [
    {
        "id": "lin",
        "name": "林",
        "source": "dify",
        "description": "默认对话/RAG 助手，占位同步 Dify tools。",
        "tags": ["chat", "rag"],
    }
]


class PostCreate(BaseModel):
    user_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=160)
    body: str = Field(..., min_length=1, max_length=4000)
    tags: list[str] = Field(default_factory=list)


class VoteRequest(BaseModel):
    value: VoteValue
    reason: str = Field(..., min_length=3, max_length=500)
    user_id: uuid.UUID | None = None


class DebateCreate(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    summary: str = Field("", max_length=1000)
    created_by: uuid.UUID | None = None


class DebateCommentCreate(BaseModel):
    stance: Literal["pro", "con"]
    body: str = Field(..., min_length=1, max_length=2000)
    user_id: uuid.UUID | None = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("/im/status")
async def im_status():
    return {
        "provider": "OpenIM",
        "mode": "placeholder",
        "configured": False,
        "next": "Connect OpenIM server credentials and mobile SDK initialization.",
    }


@router.get("/square/posts")
async def list_posts(tag: str | None = Query(None)):
    items = list(_posts.values())
    if tag:
        items = [item for item in items if tag in item.get("tags", [])]
    return {"items": items}


@router.post("/square/posts", status_code=201)
async def create_post(body: PostCreate):
    post_id = str(uuid.uuid4())
    post = {
        "id": post_id,
        "user_id": str(body.user_id),
        "title": body.title,
        "body": body.body,
        "tags": body.tags,
        "votes": {"up": 0, "down": 0},
        "vote_reasons": [],
        "created_at": _now(),
    }
    _posts[post_id] = post
    return post


@router.post("/square/posts/{post_id}/vote")
async def vote_post(post_id: str, body: VoteRequest):
    post = _posts.get(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    post["votes"][body.value] += 1
    post["vote_reasons"].append(
        {
            "value": body.value,
            "reason": body.reason,
            "user_id": str(body.user_id) if body.user_id else None,
            "created_at": _now(),
        }
    )
    return post


@router.get("/debates")
async def list_debates():
    return {"items": list(_debates.values())}


@router.post("/debates", status_code=201)
async def create_debate(body: DebateCreate):
    debate_id = str(uuid.uuid4())
    debate = {
        "id": debate_id,
        "topic": body.topic,
        "summary": body.summary,
        "created_by": str(body.created_by) if body.created_by else None,
        "comments": [],
        "created_at": _now(),
    }
    _debates[debate_id] = debate
    return debate


@router.post("/debates/{debate_id}/comments", status_code=201)
async def add_debate_comment(debate_id: str, body: DebateCommentCreate):
    debate = _debates.get(debate_id)
    if debate is None:
        raise HTTPException(status_code=404, detail="Debate not found")
    comment = {
        "id": str(uuid.uuid4()),
        "stance": body.stance,
        "body": body.body,
        "user_id": str(body.user_id) if body.user_id else None,
        "created_at": _now(),
        "pin_score": 1 if body.stance == "pro" else 0,
    }
    debate["comments"].append(comment)
    debate["comments"].sort(key=lambda item: item["pin_score"], reverse=True)
    return comment


@router.get("/market/agents")
async def market_agents():
    return {
        "mode": "placeholder",
        "source": "Dify tools sync",
        "items": _market_agents,
    }


@router.get("/search")
async def search(q: str = Query(..., min_length=1)):
    q_lower = q.lower()
    post_hits = [
        post
        for post in _posts.values()
        if q_lower in post["title"].lower() or q_lower in post["body"].lower()
    ]
    debate_hits = [
        debate
        for debate in _debates.values()
        if q_lower in debate["topic"].lower() or q_lower in debate["summary"].lower()
    ]
    return {
        "engine": "meilisearch-placeholder",
        "query": q,
        "items": {"posts": post_hits, "debates": debate_hits},
    }


@router.get("/profiles/{user_id}")
async def profile(user_id: uuid.UUID):
    return {
        "user_id": str(user_id),
        "works": [],
        "likes": [],
        "collections": [],
        "tags": ["探索者"],
        "mode": "placeholder",
    }
