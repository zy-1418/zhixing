from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from config import settings

router = APIRouter(prefix="/extensions", tags=["extensions"])
compat_router = APIRouter(tags=["extensions-compat"])


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


@compat_router.get("/openim/status")
@router.get("/openim/status")
async def openim_status():
    return {
        "service": "OpenIM",
        "status": "placeholder",
        "docs": "docs/OPENIM.md",
        "capabilities": ["friends", "groups", "team-chat"],
    }


@compat_router.get("/workflows/definition")
async def workflow_definition():
    return {
        "engine": "react-flow-webview",
        "schema": {
            "nodes": [{"id": "start", "type": "input", "data": {"label": "开始"}}],
            "edges": [],
        },
        "status": "placeholder",
    }


@compat_router.post("/workflows")
@router.post("/workflows")
async def save_workflow(definition: WorkflowDefinition):
    return {
        "status": "saved-placeholder",
        "engine": "react-flow-webview",
        "definition": definition.model_dump(),
    }


@compat_router.get("/market/agents")
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


@compat_router.post("/search/index")
@router.post("/search/index")
async def index_documents(body: SearchIndexRequest):
    return {
        "status": "accepted-placeholder",
        "meili_url": settings.meili_url,
        "collection": body.collection,
        "count": len(body.documents),
    }


@compat_router.get("/search")
@router.get("/search")
async def search(q: str):
    return {
        "query": q,
        "blocked": True,
        "reason": "Meilisearch is not available in Cursor Cloud; contract is ready.",
        "items": [],
    }


@compat_router.get("/profile/{user_id}")
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


@compat_router.get("/knowledge/graph")
@router.get("/knowledge/graph")
async def knowledge_graph(user_id: str | None = None):
    return {
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "user_id": user_id,
        "nodes": [],
        "edges": [],
    }


@compat_router.get("/graph/notes/{note_id}")
async def note_graph(note_id: str):
    return {
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "note_id": note_id,
        "nodes": [],
        "edges": [],
        "status": "placeholder",
    }


@compat_router.get("/friend-ai/personas")
async def friend_ai_personas(user_id: str | None = None):
    return {
        "blocked": True,
        "qdrant_url": settings.qdrant_url,
        "user_id": user_id,
        "items": [],
        "status": "placeholder",
    }


@compat_router.get("/miniprograms")
async def list_miniprograms():
    return {
        "items": [],
        "workflow_engine": "Dify Workflow",
        "sandbox": "e2b-placeholder",
        "status": "placeholder",
    }


@compat_router.post("/miniprograms/generate")
@router.post("/mini-programs/generate")
async def generate_mini_program(body: MiniProgramRequest):
    return {
        "status": "placeholder",
        "prompt": body.prompt,
        "dify_workflow_id": body.dify_workflow_id,
        "sandbox": "e2b-placeholder",
    }


@compat_router.get("/canvas/templates")
@router.get("/canvas/templates")
async def canvas_templates():
    return {
        "templates": [
            {"id": "tldraw-blank", "name": "无限画布", "engine": "tldraw"},
            {"id": "dual-pdf", "name": "双联 PDF 阅读", "engine": "pdf.js"},
        ]
    }


@compat_router.get("/dual-pdf/layout")
async def dual_pdf_layout():
    return {
        "engine": "pdf.js",
        "layout": "dual-column",
        "panes": ["source-pdf", "notes"],
        "status": "placeholder",
    }


@compat_router.get("/commerce/status")
@router.get("/commerce/status")
async def commerce_status():
    return {
        "blocked": True,
        "medusa_api_url": settings.medusa_api_url,
        "capabilities": ["orders", "cart", "wallet"],
    }


@compat_router.get("/desktop/status")
@router.get("/desktop/status")
async def desktop_status():
    return {
        "status": "placeholder",
        "targets": ["flutter-desktop", "tauri"],
        "scripts": ["scripts/build-desktop.sh"],
    }
