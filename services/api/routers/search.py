from __future__ import annotations

from typing import Any, Literal

import httpx
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from models.note import Note
from models.social_post import SocialPost

router = APIRouter(prefix="/search", tags=["search"])

SearchType = Literal["all", "notes", "posts"]


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.meili_master_key}"}


async def _db_search(q: str, search_type: SearchType, db: AsyncSession) -> dict[str, Any]:
    hits: list[dict[str, Any]] = []
    pattern = f"%{q}%"

    if search_type in ("all", "notes"):
        notes = await db.scalars(select(Note).where(Note.title.ilike(pattern)))
        hits.extend(
            {
                "type": "note",
                "id": str(note.id),
                "title": note.title,
                "summary": f"{len(note.blocks)} blocks",
            }
            for note in notes
        )

    if search_type in ("all", "posts"):
        posts = await db.scalars(
            select(SocialPost).where(
                or_(SocialPost.title.ilike(pattern), SocialPost.content.ilike(pattern))
            )
        )
        hits.extend(
            {
                "type": "post",
                "id": str(post.id),
                "title": post.title,
                "summary": post.content[:160],
            }
            for post in posts
        )

    return {"mode": "database-fallback", "query": q, "hits": hits}


@router.get("")
async def search(
    q: str = Query(..., min_length=1),
    type: SearchType = Query("all"),
    db: AsyncSession = Depends(get_db),
):
    payload = {"q": q, "limit": 20}
    index = "zhixing_all" if type == "all" else f"zhixing_{type}"
    url = f"{settings.meili_host.rstrip('/')}/indexes/{index}/search"
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.post(url, headers=_headers(), json=payload)
        response.raise_for_status()
        return {"mode": "meilisearch", **response.json()}
    except Exception:
        return await _db_search(q, type, db)


@router.post("/reindex")
async def reindex(db: AsyncSession = Depends(get_db)):
    notes = list(await db.scalars(select(Note)))
    posts = list(await db.scalars(select(SocialPost)))
    documents = [
        {
            "id": f"note:{note.id}",
            "type": "note",
            "title": note.title,
            "content": str(note.blocks),
        }
        for note in notes
    ] + [
        {
            "id": f"post:{post.id}",
            "type": "post",
            "title": post.title,
            "content": post.content,
            "tags": post.tags,
        }
        for post in posts
    ]

    url = f"{settings.meili_host.rstrip('/')}/indexes/zhixing_all/documents"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, headers=_headers(), json=documents)
        response.raise_for_status()
        return {"mode": "meilisearch", "indexed": len(documents), "task": response.json()}
    except Exception as exc:
        return {
            "mode": "placeholder",
            "status": "skipped",
            "reason": f"Meilisearch unavailable: {exc}",
            "indexed": 0,
            "would_index": len(documents),
        }
