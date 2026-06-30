from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from config import settings

router = APIRouter(tags=["extensions"])


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
@router.get("/extensions/openim/status")
async def openim_status():
    return {
        "service": "OpenIM",
        "status": "placeholder",
        "docs": "docs/OPENIM.md",
        "capabilities": ["friends", "groups", "team-chat"],
    }


@router.get("/workflows/templates")
@router.get("/extensions/workflows/templates")
async def workflow_templates():
    return {
        "engine": "react-flow-webview",
        "templates": [
            {
                "id": "research-sop",
                "name": "研究型 SOP",
                "nodes": ["input", "search", "draft", "review", "archive"],
            },
            {
                "id": "writing-sop",
                "name": "写作型 SOP",
                "nodes": ["outline", "draft", "polish", "publish"],
            },
        ],
    }


@router.post("/workflows")
@router.post("/extensions/workflows")
async def save_workflow(definition: WorkflowDefinition):
    return {
        "status": "saved-placeholder",
        "engine": "react-flow-webview",
        "definition": definition.model_dump(),
    }


@router.get("/market/agents")
@router.get("/extensions/market/agents")
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
@router.post("/extensions/search/index")
async def index_documents(body: SearchIndexRequest):
    return {
        "status": "accepted-placeholder",
        "meili_url": settings.meili_url,
        "collection": body.collection,
        "count": len(body.documents),
    }


@router.get("/search")
@router.get("/extensions/search")
async def search(q: str):
    return {
        "query": q,
        "blocked": True,
        "reason": "Meilisearch is not available in Cursor Cloud; contract is ready.",
        "items": [],
    }


@router.get("/profile/{user_id}")
@router.get("/profiles/{user_id}")
@router.get("/extensions/profile/{user_id}")
@router.get("/extensions/profiles/{user_id}")
async def profile(user_id: str):
    return {
        "user_id": user_id,
        "works": [],
        "likes": [],
        "collections": [],
        "tags": [],
        "status": "placeholder",
    }


@router.get("/graph/status")
@router.get("/extensions/graph/status")
async def graph_status():
    return {
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "pipeline": "note-relation-extraction-placeholder",
        "ui": "sigma.js-webview",
    }


@router.get("/knowledge/graph")
@router.get("/extensions/knowledge/graph")
async def knowledge_graph(user_id: str | None = None):
    return {
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "user_id": user_id,
        "nodes": [],
        "edges": [],
    }


@router.get("/friend-ai/status")
@router.get("/extensions/friend-ai/status")
async def friend_ai_status():
    return {
        "blocked": True,
        "qdrant_url": settings.qdrant_url,
        "strategy": "per-user-rag-collection-placeholder",
        "capabilities": ["friend-switching", "note-distillation", "rag-chat"],
    }


@router.get("/miniprograms/status")
@router.get("/mini-programs/status")
@router.get("/extensions/miniprograms/status")
@router.get("/extensions/mini-programs/status")
async def miniprograms_status():
    return {
        "status": "placeholder",
        "engine": "Dify Workflow + e2b sandbox",
        "blocked": not bool(settings.dify_api_key),
    }


@router.post("/mini-programs/generate")
@router.post("/extensions/mini-programs/generate")
async def generate_mini_program(body: MiniProgramRequest):
    return {
        "status": "placeholder",
        "prompt": body.prompt,
        "dify_workflow_id": body.dify_workflow_id,
        "sandbox": "e2b-placeholder",
    }


@router.get("/canvas/templates")
@router.get("/extensions/canvas/templates")
async def canvas_templates():
    return {
        "templates": [
            {"id": "tldraw-blank", "name": "无限画布", "engine": "tldraw"},
            {"id": "dual-pdf", "name": "双联 PDF 阅读", "engine": "pdf.js"},
        ]
    }


@router.get("/dual-pdf/templates")
@router.get("/extensions/dual-pdf/templates")
async def dual_pdf_templates():
    return {
        "templates": [
            {
                "id": "dual-pdf-default",
                "name": "双联 PDF 阅读",
                "engine": "pdf.js",
                "layout": "left-pdf-right-notes",
            }
        ]
    }


@router.get("/commerce/status")
@router.get("/extensions/commerce/status")
async def commerce_status():
    return {
        "blocked": True,
        "medusa_api_url": settings.medusa_api_url,
        "capabilities": ["orders", "cart", "wallet"],
    }


@router.get("/desktop/status")
@router.get("/extensions/desktop/status")
async def desktop_status():
    return {
        "status": "placeholder",
        "targets": ["flutter-desktop", "tauri"],
        "scripts": ["scripts/build-desktop.sh"],
    }
