from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/social", tags=["social"])

VoteValue = Literal["up", "down"]
DebateSide = Literal["pro", "con"]

_posts: dict[uuid.UUID, dict] = {}
_votes: list[dict] = []
_debates: dict[uuid.UUID, dict] = {}
_comments: list[dict] = []


class PostCreate(BaseModel):
    author_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=160)
    body: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)


class VoteCreate(BaseModel):
    user_id: uuid.UUID
    value: VoteValue
    reason: str = Field(..., min_length=3, max_length=500)


class DebateCreate(BaseModel):
    post_id: uuid.UUID | None = None
    topic: str = Field(..., min_length=1, max_length=200)
    thesis: str = Field(..., min_length=1)


class DebateCommentCreate(BaseModel):
    user_id: uuid.UUID
    side: DebateSide
    body: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=3, max_length=500)


@router.get("/posts")
async def list_posts():
    return sorted(_posts.values(), key=lambda item: item["created_at"], reverse=True)


@router.post("/posts", status_code=201)
async def create_post(body: PostCreate):
    post_id = uuid.uuid4()
    post = {
        "id": str(post_id),
        **body.model_dump(mode="json"),
        "score": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _posts[post_id] = post
    return post


@router.post("/posts/{post_id}/votes", status_code=201)
async def vote_post(post_id: uuid.UUID, body: VoteCreate):
    post = _posts.get(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    delta = 1 if body.value == "up" else -1
    post["score"] += delta
    vote = {
        "post_id": str(post_id),
        **body.model_dump(mode="json"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _votes.append(vote)
    return vote


@router.post("/debates", status_code=201)
async def create_debate(body: DebateCreate):
    debate_id = uuid.uuid4()
    debate = {
        "id": str(debate_id),
        **body.model_dump(mode="json"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _debates[debate_id] = debate
    return debate


@router.get("/debates/{debate_id}")
async def get_debate(debate_id: uuid.UUID):
    debate = _debates.get(debate_id)
    if debate is None:
        raise HTTPException(status_code=404, detail="Debate not found")
    related = [item for item in _comments if item["debate_id"] == str(debate_id)]
    related.sort(key=lambda item: (item["side"], -len(item["reason"])))
    return {**debate, "comments": related}


@router.post("/debates/{debate_id}/comments", status_code=201)
async def create_debate_comment(debate_id: uuid.UUID, body: DebateCommentCreate):
    if debate_id not in _debates:
        raise HTTPException(status_code=404, detail="Debate not found")
    comment = {
        "id": str(uuid.uuid4()),
        "debate_id": str(debate_id),
        **body.model_dump(mode="json"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _comments.append(comment)
    return comment
