from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from config import settings

router = APIRouter(prefix="/extensions", tags=["extensions"])


class WorkflowDefinition(BaseModel):
    name: str
    nodes: list[dict[str, Any]] = Field(default_factory=list)
    edges: list[dict[str, Any]] = Field(default_factory=list)


class SearchIndexRequest(BaseModel):
    collection: str
    documents: list[dict[str, Any]] = Field(default_factory=list)


class MiniProgramRequest(BaseModel):
    prompt: str
    dify_workflow_id: str | None = None
    inputs: dict[str, Any] = Field(default_factory=dict)


class FriendAiSwitchRequest(BaseModel):
    user_id: str
    friend_id: str
    mode: str = "rag"


class DesktopBuildRequest(BaseModel):
    target: str = "flutter-desktop"
    channel: str = "stable"


@router.get("/openim/status")
async def openim_status():
    return {
        "service": "OpenIM",
        "status": "placeholder",
        "docs": "docs/OPENIM.md",
        "capabilities": ["friends", "groups", "team-chat"],
    }


@router.post("/workflows")
async def save_workflow(definition: WorkflowDefinition):
    return {
        "status": "saved-placeholder",
        "engine": "react-flow-webview",
        "definition": definition.model_dump(),
    }


@router.get("/market/agents")
async def list_market_agents():
    return {
        "blocked": not bool(settings.dify_api_key),
        "source": "Dify tools marketplace",
        "items": [
            {
                "id": "lin",
                "name": "林",
                "description": "知行 MVP 默认对话/RAG Agent，占位同步 Dify 工具。",
                "enabled": bool(settings.dify_api_key),
            }
        ],
    }


@router.post("/search/index")
async def index_documents(body: SearchIndexRequest):
    return {
        "status": "accepted-placeholder",
        "meili_url": settings.meili_url,
        "collection": body.collection,
        "count": len(body.documents),
    }


@router.get("/search")
async def search(q: str):
    return {
        "query": q,
        "blocked": True,
        "reason": "Meilisearch is not available in Cursor Cloud; contract is ready.",
        "items": [],
    }


@router.get("/profile/{user_id}")
async def profile_alias(user_id: str):
    return await profile(user_id)


@router.get("/profiles/{user_id}")
async def profile(user_id: str):
    return {
        "user_id": user_id,
        "works": [],
        "likes": [],
        "collections": [],
        "tags": [],
        "status": "placeholder",
    }


@router.get("/knowledge/graph")
async def knowledge_graph(user_id: str | None = None):
    return {
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "user_id": user_id,
        "nodes": [],
        "edges": [],
    }


@router.get("/graph/notes/{note_id}")
async def note_graph(note_id: str):
    return {
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "note_id": note_id,
        "nodes": [],
        "edges": [],
        "pipeline": "note-relation-extraction-placeholder",
    }


@router.get("/graph/sigma")
async def sigma_graph():
    return {
        "status": "placeholder",
        "engine": "sigma.js-webview",
        "nodes": [],
        "edges": [],
    }


@router.post("/friend-ai/switch")
async def switch_friend_ai(body: FriendAiSwitchRequest):
    return {
        "status": "placeholder",
        "user_id": body.user_id,
        "friend_id": body.friend_id,
        "mode": body.mode,
        "qdrant_url": settings.qdrant_url,
    }


@router.post("/miniprograms")
async def miniprograms_alias(body: MiniProgramRequest):
    return await generate_mini_program(body)


@router.post("/mini-programs/generate")
async def generate_mini_program(body: MiniProgramRequest):
    return {
        "status": "placeholder",
        "prompt": body.prompt,
        "dify_workflow_id": body.dify_workflow_id,
        "sandbox": "e2b-placeholder",
    }


@router.get("/canvas/templates")
async def canvas_templates():
    return {
        "templates": [
            {"id": "tldraw-blank", "name": "无限画布", "engine": "tldraw"},
            {"id": "dual-pdf", "name": "双联 PDF 阅读", "engine": "pdf.js"},
        ]
    }


@router.get("/canvas/templates/tldraw")
async def tldraw_template():
    return {
        "id": "tldraw-blank",
        "name": "无限画布",
        "engine": "tldraw",
        "status": "placeholder",
    }


@router.get("/pdf/dual-reader")
async def dual_pdf_reader():
    return {
        "id": "dual-pdf",
        "name": "双联 PDF 阅读",
        "engine": "pdf.js",
        "status": "placeholder",
    }


@router.get("/commerce/status")
async def commerce_status():
    return {
        "blocked": True,
        "medusa_api_url": settings.medusa_api_url,
        "capabilities": ["orders", "cart", "wallet"],
    }


@router.get("/desktop/status")
async def desktop_status():
    return {
        "status": "placeholder",
        "targets": ["flutter-desktop", "tauri"],
        "scripts": ["scripts/build-desktop.sh"],
    }


@router.post("/desktop/builds")
async def create_desktop_build(body: DesktopBuildRequest):
    return {
        "status": "blocked",
        "reason": "Flutter/Tauri toolchains are unavailable in Cursor Cloud.",
        "target": body.target,
        "channel": body.channel,
        "scripts": ["scripts/build-desktop.sh"],
    }


@router.get("/offline/notes")
async def offline_notes(limit: int = 23):
    return {
        "status": "placeholder",
        "limit": limit,
        "items": [],
        "strategy": "cache latest notes for offline reading",
    }
