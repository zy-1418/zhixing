from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from config import settings

router = APIRouter(prefix="/extensions", tags=["extensions"])
compatibility_router = APIRouter(tags=["compatibility"])


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


@compatibility_router.get("/openim/status")
@router.get("/openim/status")
async def openim_status():
    return {
        "service": "OpenIM",
        "status": "placeholder",
        "docs": "docs/OPENIM.md",
        "capabilities": ["friends", "groups", "team-chat"],
    }


@compatibility_router.get("/workflows/templates")
@router.get("/workflows/templates")
async def workflow_templates():
    return {
        "engine": "react-flow-webview",
        "templates": [
            {
                "id": "research-sop",
                "name": "研究型 SOP",
                "nodes": ["检索", "初稿", "审查", "校验"],
            },
            {
                "id": "writing-sop",
                "name": "写作型 SOP",
                "nodes": ["大纲", "起草", "润色", "校对"],
            },
        ],
    }


@compatibility_router.post("/workflows")
@router.post("/workflows")
async def save_workflow(definition: WorkflowDefinition):
    return {
        "status": "saved-placeholder",
        "engine": "react-flow-webview",
        "definition": definition.model_dump(),
    }


@compatibility_router.get("/market/agents")
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


@compatibility_router.post("/search/index")
@router.post("/search/index")
async def index_documents(body: SearchIndexRequest):
    return {
        "status": "accepted-placeholder",
        "meili_url": settings.meili_url,
        "collection": body.collection,
        "count": len(body.documents),
    }


@compatibility_router.get("/search")
@router.get("/search")
async def search(q: str):
    return {
        "query": q,
        "blocked": True,
        "reason": "Meilisearch is not available in Cursor Cloud; contract is ready.",
        "items": [],
    }


@compatibility_router.get("/profiles/{user_id}")
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


@compatibility_router.get("/knowledge/graph")
@router.get("/knowledge/graph")
async def knowledge_graph(user_id: str | None = None):
    return {
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "user_id": user_id,
        "nodes": [],
        "edges": [],
    }


@compatibility_router.get("/friend-ai/status")
@router.get("/friend-ai/status")
async def friend_ai_status(user_id: str | None = None):
    return {
        "blocked": True,
        "user_id": user_id,
        "qdrant_url": settings.qdrant_url,
        "collections": [],
        "reason": "Qdrant/Dify are not available in Cursor Cloud; API contract is ready.",
    }


@compatibility_router.post("/miniprograms/generate")
@router.post("/mini-programs/generate")
async def generate_mini_program(body: MiniProgramRequest):
    return {
        "status": "placeholder",
        "prompt": body.prompt,
        "dify_workflow_id": body.dify_workflow_id,
        "sandbox": "e2b-placeholder",
    }


@compatibility_router.get("/canvas/templates")
@router.get("/canvas/templates")
async def canvas_templates():
    return {
        "templates": [
            {"id": "tldraw-blank", "name": "无限画布", "engine": "tldraw"},
            {"id": "dual-pdf", "name": "双联 PDF 阅读", "engine": "pdf.js"},
        ]
    }


@compatibility_router.get("/dual-pdf/templates")
@router.get("/dual-pdf/templates")
async def dual_pdf_templates():
    return {
        "engine": "pdf.js",
        "templates": [
            {
                "id": "dual-pdf-study",
                "name": "双联 PDF 阅读",
                "panes": ["pdf", "notes"],
            }
        ],
    }


@compatibility_router.get("/commerce/status")
@router.get("/commerce/status")
async def commerce_status():
    return {
        "blocked": True,
        "medusa_api_url": settings.medusa_api_url,
        "capabilities": ["orders", "cart", "wallet"],
    }


@compatibility_router.get("/cart")
@router.get("/commerce/cart")
async def cart_status(user_id: str | None = None):
    return {
        "blocked": True,
        "user_id": user_id,
        "items": [],
        "wallet": {"balance": 0, "currency": "CNY"},
        "reason": "Medusa is not available in Cursor Cloud; API contract is ready.",
    }


@compatibility_router.get("/desktop/status")
@router.get("/desktop/status")
async def desktop_status():
    return {
        "status": "placeholder",
        "targets": ["flutter-desktop", "tauri"],
        "scripts": ["scripts/build-desktop.sh"],
    }
