from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from config import settings

router = APIRouter(tags=["contracts"])

_debates: dict[str, dict[str, Any]] = {}


class DebateCreate(BaseModel):
    post_id: str | None = None
    topic: str = Field(..., min_length=1, max_length=240)
    summary: str = ""


def _now() -> str:
    return datetime.now(UTC).isoformat()


@router.get("/openim/status")
async def openim_status():
    return {
        "service": "OpenIM",
        "status": "placeholder",
        "docs": "docs/OPENIM.md",
        "capabilities": ["friends", "groups", "team-chat"],
    }


@router.get("/workflows/templates")
async def workflow_templates():
    return {
        "engine": "react-flow-webview",
        "templates": [
            {
                "id": "research-sop",
                "name": "Research SOP",
                "nodes": ["brief", "search", "draft", "review"],
            },
            {
                "id": "writing-sop",
                "name": "Writing SOP",
                "nodes": ["outline", "draft", "polish", "qa"],
            },
        ],
    }


@router.get("/market/agents")
async def list_market_agents():
    return {
        "blocked": not bool(settings.dify_api_key),
        "source": "Dify tools marketplace",
        "items": [
            {
                "id": "lin",
                "name": "Lin",
                "description": "Default Zhixing conversation/RAG agent placeholder.",
                "enabled": bool(settings.dify_api_key),
            }
        ],
    }


@router.get("/search")
async def search(q: str = Query("", description="Search keyword")):
    return {
        "query": q,
        "blocked": True,
        "reason": "Meilisearch is not available in Cursor Cloud; contract is ready.",
        "items": [],
    }


@router.get("/profile")
async def profile(user_id: str | None = None):
    return {
        "user_id": user_id,
        "works": [],
        "likes": [],
        "collections": [],
        "tags": [],
        "status": "placeholder",
    }


@router.get("/graph/status")
async def graph_status():
    return {
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "pipeline": "note-relation-extraction-placeholder",
        "viewer": "sigma.js",
    }


@router.get("/friends/ai-personas")
async def friend_ai_personas(user_id: str | None = None):
    return {
        "user_id": user_id,
        "blocked": True,
        "vector_store": "qdrant-per-user-placeholder",
        "items": [],
    }


@router.get("/miniprograms/templates")
async def miniprogram_templates():
    return {
        "sandbox": "e2b-placeholder",
        "workflow_engine": "Dify Workflow",
        "templates": [
            {"id": "chat-tool", "name": "Chat Tool"},
            {"id": "research-widget", "name": "Research Widget"},
        ],
    }


@router.get("/canvas/templates")
async def canvas_templates():
    return {
        "templates": [
            {"id": "tldraw-blank", "name": "Infinite Canvas", "engine": "tldraw"},
            {"id": "mindmap", "name": "Mind Map", "engine": "tldraw"},
        ]
    }


@router.get("/pdf/templates/dual")
async def dual_pdf_templates():
    return {
        "engine": "pdf.js",
        "templates": [
            {
                "id": "dual-reader",
                "name": "Dual PDF Reader",
                "panes": ["source-pdf", "notes"],
            }
        ],
    }


@router.get("/commerce/status")
async def commerce_status():
    return {
        "blocked": True,
        "medusa_api_url": settings.medusa_api_url,
        "capabilities": ["orders", "cart", "wallet"],
    }


@router.get("/commerce/cart")
async def commerce_cart(user_id: str | None = None):
    return {
        "user_id": user_id,
        "blocked": True,
        "reason": "Medusa is not available in Cursor Cloud; cart contract is ready.",
        "items": [],
        "total": 0,
    }


@router.get("/desktop/status")
async def desktop_status():
    return {
        "status": "placeholder",
        "targets": ["flutter-desktop", "tauri"],
        "scripts": ["scripts/build-desktop.sh"],
    }


@router.get("/debates")
async def list_debates():
    return sorted(_debates.values(), key=lambda item: item["created_at"], reverse=True)


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
