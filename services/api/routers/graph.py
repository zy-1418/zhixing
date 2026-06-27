from __future__ import annotations

import re
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.note import Note

router = APIRouter(prefix="/graph", tags=["graph"])

ENTITY_RE = re.compile(r"(?:#|@)([\w\u4e00-\u9fff-]{2,40})")


def _block_text(blocks: list[Any]) -> str:
    parts: list[str] = []
    for block in blocks:
        if isinstance(block, dict):
            text = block.get("text")
            if text:
                parts.append(str(text))
        else:
            parts.append(str(block))
    return "\n".join(parts)


@router.post("/notes/{note_id}/extract")
async def extract_note_relations(
    note_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    note = await db.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    text = _block_text(note.blocks)
    entities = sorted(set(ENTITY_RE.findall(text)))
    edges = [
        {
            "source": str(note.id),
            "target": entity,
            "relation": "MENTIONS",
        }
        for entity in entities
    ]
    return {
        "mode": "extraction-placeholder",
        "note_id": str(note.id),
        "title": note.title,
        "nodes": [{"id": str(note.id), "label": note.title, "type": "note"}]
        + [{"id": entity, "label": entity, "type": "entity"} for entity in entities],
        "edges": edges,
        "neo4j": {
            "status": "skipped",
            "reason": "Cloud environment does not run Neo4j/Docker.",
        },
    }


@router.get("/preview")
async def graph_preview():
    return {
        "nodes": [
            {"id": "notes", "label": "笔记", "type": "collection"},
            {"id": "topics", "label": "主题", "type": "collection"},
            {"id": "questions", "label": "研究问题", "type": "collection"},
        ],
        "edges": [
            {"source": "notes", "target": "topics", "relation": "MENTIONS"},
            {"source": "topics", "target": "questions", "relation": "INSPIRES"},
        ],
    }
