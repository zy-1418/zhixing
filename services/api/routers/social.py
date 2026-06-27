from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.social_post import SocialPost
from models.social_vote import SocialVote

router = APIRouter(prefix="/social", tags=["social"])

VoteType = Literal["up", "down"]


class SocialPostCreate(BaseModel):
    user_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=256)
    content: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)


class SocialPostResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    content: str
    tags: list
    score: int = 0
    up_votes: int = 0
    down_votes: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VoteRequest(BaseModel):
    user_id: uuid.UUID
    vote_type: VoteType
    reason: str = Field(..., min_length=1, max_length=1000)


class VoteResponse(BaseModel):
    post_id: uuid.UUID
    user_id: uuid.UUID
    vote_type: VoteType
    reason: str
    score: int
    up_votes: int
    down_votes: int


async def _vote_counts(post_id: uuid.UUID, db: AsyncSession) -> tuple[int, int]:
    up_votes = await db.scalar(
        select(func.count()).where(
            SocialVote.post_id == post_id, SocialVote.vote_type == "up"
        )
    )
    down_votes = await db.scalar(
        select(func.count()).where(
            SocialVote.post_id == post_id, SocialVote.vote_type == "down"
        )
    )
    return int(up_votes or 0), int(down_votes or 0)


async def _post_response(post: SocialPost, db: AsyncSession) -> SocialPostResponse:
    up_votes, down_votes = await _vote_counts(post.id, db)
    return SocialPostResponse.model_validate(post).model_copy(
        update={
            "up_votes": up_votes,
            "down_votes": down_votes,
            "score": up_votes - down_votes,
        }
    )


@router.get("/posts", response_model=list[SocialPostResponse])
async def list_posts(
    tag: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SocialPost).order_by(SocialPost.created_at.desc())
    if tag:
        stmt = stmt.where(SocialPost.tags.contains([tag]))
    posts = list(await db.scalars(stmt))
    return [await _post_response(post, db) for post in posts]


@router.post("/posts", response_model=SocialPostResponse, status_code=201)
async def create_post(
    body: SocialPostCreate, db: AsyncSession = Depends(get_db)
):
    post = SocialPost(**body.model_dump())
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return await _post_response(post, db)


@router.get("/posts/{post_id}", response_model=SocialPostResponse)
async def get_post(post_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    post = await db.get(SocialPost, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return await _post_response(post, db)


@router.post("/posts/{post_id}/votes", response_model=VoteResponse)
async def vote_post(
    post_id: uuid.UUID, body: VoteRequest, db: AsyncSession = Depends(get_db)
):
    post = await db.get(SocialPost, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    vote = await db.scalar(
        select(SocialVote).where(
            SocialVote.post_id == post_id, SocialVote.user_id == body.user_id
        )
    )
    if vote is None:
        vote = SocialVote(
            post_id=post_id,
            user_id=body.user_id,
            vote_type=body.vote_type,
            reason=body.reason,
        )
        db.add(vote)
    else:
        vote.vote_type = body.vote_type
        vote.reason = body.reason

    await db.commit()
    up_votes, down_votes = await _vote_counts(post_id, db)
    return VoteResponse(
        post_id=post_id,
        user_id=body.user_id,
        vote_type=body.vote_type,
        reason=body.reason,
        up_votes=up_votes,
        down_votes=down_votes,
        score=up_votes - down_votes,
    )
