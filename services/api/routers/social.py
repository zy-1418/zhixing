from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/social", tags=["social"])
compat_router = APIRouter(tags=["social"])

VoteType = Literal["up", "down"]
Side = Literal["pro", "con"]

_posts: dict[str, dict] = {}
_votes: list[dict] = []
_debates: dict[str, dict] = {}


class PostCreate(BaseModel):
    author_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=160)
    content: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)


class VoteCreate(BaseModel):
    user_id: uuid.UUID
    vote_type: VoteType
    reason: str = Field(..., min_length=3, description="赞/踩必须填写理由")


class DebateCreate(BaseModel):
    post_id: str | None = None
    topic: str = Field(..., min_length=1, max_length=240)
    summary: str = ""


class DebateCommentCreate(BaseModel):
    user_id: uuid.UUID
    side: Side
    content: str = Field(..., min_length=1)
    evidence_urls: list[str] = Field(default_factory=list)


def _now() -> str:
    return datetime.now(UTC).isoformat()


@router.get("/posts")
async def list_posts(tag: str | None = Query(None)):
    posts = list(_posts.values())
    if tag:
        posts = [post for post in posts if tag in post.get("tags", [])]
    return sorted(posts, key=lambda item: item["created_at"], reverse=True)


@router.post("/posts", status_code=201)
async def create_post(body: PostCreate):
    post_id = str(uuid.uuid4())
    post = {
        "id": post_id,
        "author_id": str(body.author_id),
        "title": body.title,
        "content": body.content,
        "tags": body.tags,
        "score": 0,
        "created_at": _now(),
    }
    _posts[post_id] = post
    return post


@router.post("/posts/{post_id}/votes", status_code=201)
async def vote_post(post_id: str, body: VoteCreate):
    post = _posts.get(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    delta = 1 if body.vote_type == "up" else -1
    post["score"] += delta
    vote = {
        "post_id": post_id,
        "user_id": str(body.user_id),
        "vote_type": body.vote_type,
        "reason": body.reason,
        "created_at": _now(),
    }
    _votes.append(vote)
    return {"post": post, "vote": vote}


@router.post("/posts/{post_id}/vote", status_code=201)
async def vote_post_alias(post_id: str, body: VoteCreate):
    return await vote_post(post_id, body)


@compat_router.get("/debates")
async def list_root_debates():
    return sorted(_debates.values(), key=lambda item: item["created_at"], reverse=True)


@compat_router.post("/debates", status_code=201)
async def create_root_debate(body: DebateCreate):
    return await create_debate(body)


@router.post("/debates", status_code=201)
async def create_debate(body: DebateCreate):
    debate_id = str(uuid.uuid4())
    debate = {
        "id": debate_id,
        "post_id": body.post_id,
        "topic": body.topic,
        "summary": body.summary,
        "comments": [],
        "created_at": _now(),
    }
    _debates[debate_id] = debate
    return debate


@router.get("/debates/{debate_id}")
async def get_debate(debate_id: str):
    debate = _debates.get(debate_id)
    if debate is None:
        raise HTTPException(status_code=404, detail="Debate not found")
    comments = sorted(
        debate["comments"],
        key=lambda item: (len(item.get("evidence_urls", [])), item["created_at"]),
        reverse=True,
    )
    return {**debate, "comments": comments}


@router.post("/debates/{debate_id}/comments", status_code=201)
async def add_debate_comment(debate_id: str, body: DebateCommentCreate):
    debate = _debates.get(debate_id)
    if debate is None:
        raise HTTPException(status_code=404, detail="Debate not found")
    comment = {
        "id": str(uuid.uuid4()),
        "user_id": str(body.user_id),
        "side": body.side,
        "content": body.content,
        "evidence_urls": body.evidence_urls,
        "created_at": _now(),
    }
    debate["comments"].append(comment)
    return comment
