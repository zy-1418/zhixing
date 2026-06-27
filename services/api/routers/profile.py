from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.note import Note
from models.social_post import SocialPost
from models.social_vote import SocialVote
from models.user import User

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/{user_id}")
async def get_profile(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    notes = list(await db.scalars(select(Note).where(Note.user_id == user_id)))
    posts = list(
        await db.scalars(select(SocialPost).where(SocialPost.user_id == user_id))
    )
    liked_votes = list(
        await db.scalars(
            select(SocialVote).where(
                SocialVote.user_id == user_id, SocialVote.vote_type == "up"
            )
        )
    )

    tag_set = set(user.tags or [])
    for post in posts:
        tag_set.update(post.tags or [])

    works: list[dict[str, Any]] = [
        {"type": "note", "id": str(note.id), "title": note.title}
        for note in notes[:10]
    ] + [
        {"type": "post", "id": str(post.id), "title": post.title}
        for post in posts[:10]
    ]

    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
        "level": user.level,
        "tags": sorted(tag_set),
        "stats": {
            "notes": len(notes),
            "posts": len(posts),
            "liked": len(liked_votes),
            "favorites": 0,
        },
        "works": works,
        "liked_post_ids": [str(vote.post_id) for vote in liked_votes],
        "favorites": [],
    }
