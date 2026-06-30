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


@compat_router.get("/openim/status")
async def openim_status_compat():
    return await openim_status()


@compat_router.get("/workflows")
async def list_workflows_compat():
    return {
        "status": "placeholder",
        "engine": "react-flow-webview",
        "items": [],
    }


@compat_router.post("/workflows")
async def save_workflow_compat(definition: WorkflowDefinition):
    return await save_workflow(definition)


@compat_router.get("/market/agents")
async def list_market_agents_compat():
    return await list_market_agents()


@compat_router.get("/search")
async def search_compat(q: str = ""):
    return await search(q)


@compat_router.get("/profile/{user_id}")
async def profile_compat(user_id: str):
    return await profile(user_id)


@compat_router.get("/graph/status")
async def graph_status_compat():
    return {
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "pipeline": "note-relation-extraction-placeholder",
        "webview": "sigma.js",
    }


@compat_router.get("/friend-ai/status")
async def friend_ai_status_compat():
    return {
        "blocked": True,
        "qdrant_url": settings.qdrant_url,
        "strategy": "per-user-collection-rag-placeholder",
    }


@compat_router.get("/miniprograms/status")
async def miniprograms_status_compat():
    return {
        "blocked": not bool(settings.dify_api_key),
        "engine": "Dify Workflow + e2b-placeholder",
        "items": [],
    }


@compat_router.get("/canvas/templates")
async def canvas_templates_compat():
    return await canvas_templates()


@compat_router.get("/dual-pdf/templates")
async def dual_pdf_templates_compat():
    return {
        "templates": [
            {
                "id": "dual-pdf",
                "name": "双联 PDF 阅读",
                "engine": "pdf.js",
                "layout": "two-pane",
            }
        ]
    }


@compat_router.get("/commerce/status")
async def commerce_status_compat():
    return await commerce_status()


@compat_router.get("/desktop/status")
async def desktop_status_compat():
    return await desktop_status()
