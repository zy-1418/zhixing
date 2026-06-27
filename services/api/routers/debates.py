from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.debate import Debate
from models.debate_comment import DebateComment

router = APIRouter(prefix="/debates", tags=["debates"])

DebateSide = Literal["pro", "con"]


class DebateCreate(BaseModel):
    user_id: uuid.UUID
    topic: str = Field(..., min_length=1, max_length=256)
    description: str = ""


class DebateCommentCreate(BaseModel):
    user_id: uuid.UUID
    side: DebateSide
    content: str = Field(..., min_length=1)
    evidence_url: str | None = Field(None, max_length=1024)
    score: int = 0


class DebateCommentResponse(BaseModel):
    id: uuid.UUID
    debate_id: uuid.UUID
    user_id: uuid.UUID
    side: str
    content: str
    evidence_url: str | None
    score: int
    is_pinned: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DebateResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    topic: str
    description: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=list[DebateResponse])
async def list_debates(db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(Debate).order_by(Debate.created_at.desc()))
    return result.all()


@router.post("", response_model=DebateResponse, status_code=201)
async def create_debate(body: DebateCreate, db: AsyncSession = Depends(get_db)):
    debate = Debate(**body.model_dump())
    db.add(debate)
    await db.commit()
    await db.refresh(debate)
    return debate


@router.get("/{debate_id}", response_model=DebateResponse)
async def get_debate(debate_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    debate = await db.get(Debate, debate_id)
    if debate is None:
        raise HTTPException(status_code=404, detail="Debate not found")
    return debate


@router.get("/{debate_id}/comments", response_model=list[DebateCommentResponse])
async def list_comments(debate_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(DebateComment)
        .where(DebateComment.debate_id == debate_id)
        .order_by(
            DebateComment.is_pinned.desc(),
            DebateComment.score.desc(),
            DebateComment.created_at.asc(),
        )
    )
    result = await db.scalars(stmt)
    return result.all()


@router.post(
    "/{debate_id}/comments",
    response_model=DebateCommentResponse,
    status_code=201,
)
async def create_comment(
    debate_id: uuid.UUID,
    body: DebateCommentCreate,
    db: AsyncSession = Depends(get_db),
):
    debate = await db.get(Debate, debate_id)
    if debate is None:
        raise HTTPException(status_code=404, detail="Debate not found")

    comment = DebateComment(debate_id=debate_id, **body.model_dump())
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


@router.post("/{debate_id}/recalculate-pins")
async def recalculate_pins(debate_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    debate = await db.get(Debate, debate_id)
    if debate is None:
        raise HTTPException(status_code=404, detail="Debate not found")

    comments = list(
        await db.scalars(
            select(DebateComment).where(DebateComment.debate_id == debate_id)
        )
    )
    for comment in comments:
        comment.is_pinned = False

    pinned: list[DebateComment] = []
    for side in ("pro", "con"):
        side_comments = [comment for comment in comments if comment.side == side]
        if side_comments:
            pinned.append(
                sorted(
                    side_comments,
                    key=lambda item: (item.score, item.created_at),
                    reverse=True,
                )[0]
            )

    for comment in pinned:
        comment.is_pinned = True

    await db.commit()
    return {
        "debate_id": str(debate_id),
        "pinned_comment_ids": [str(comment.id) for comment in pinned],
        "algorithm": "top score per side, newest wins ties",
    }
