from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from config import settings

router = APIRouter(prefix="/extensions", tags=["extensions"])
contract_router = APIRouter(tags=["extensions-contract"])


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


def _market_agents_payload() -> dict[str, Any]:
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


def _search_payload(q: str) -> dict[str, Any]:
    return {
        "query": q,
        "blocked": True,
        "reason": "Meilisearch is not available in Cursor Cloud; contract is ready.",
        "items": [],
    }


def _profile_payload(user_id: str) -> dict[str, Any]:
    return {
        "user_id": user_id,
        "works": [],
        "likes": [],
        "collections": [],
        "tags": [],
        "status": "placeholder",
    }


def _knowledge_graph_payload(user_id: str | None = None) -> dict[str, Any]:
    return {
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "user_id": user_id,
        "nodes": [],
        "edges": [],
    }


def _canvas_templates_payload() -> dict[str, Any]:
    return {
        "templates": [
            {"id": "tldraw-blank", "name": "无限画布", "engine": "tldraw"},
            {"id": "dual-pdf", "name": "双联 PDF 阅读", "engine": "pdf.js"},
        ]
    }


def _commerce_status_payload() -> dict[str, Any]:
    return {
        "blocked": True,
        "medusa_api_url": settings.medusa_api_url,
        "capabilities": ["orders", "cart", "wallet"],
    }


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
    return _market_agents_payload()


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
    return _search_payload(q)


@router.get("/profiles/{user_id}")
async def profile(user_id: str):
    return _profile_payload(user_id)


@router.get("/knowledge/graph")
async def knowledge_graph(user_id: str | None = None):
    return _knowledge_graph_payload(user_id)


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
    return _canvas_templates_payload()


@router.get("/commerce/status")
async def commerce_status():
    return _commerce_status_payload()


@router.get("/desktop/status")
async def desktop_status():
    return {
        "status": "placeholder",
        "targets": ["flutter-desktop", "tauri"],
        "scripts": ["scripts/build-desktop.sh"],
    }


@contract_router.get("/workflows/templates")
async def workflow_templates():
    return {
        "templates": [
            {
                "id": "research-sop",
                "name": "研究型 SOP",
                "engine": "react-flow-webview",
                "workflow_type": "research",
            },
            {
                "id": "writing-sop",
                "name": "写作型 SOP",
                "engine": "react-flow-webview",
                "workflow_type": "writing",
            },
            {
                "id": "search-sop",
                "name": "检索型 SOP",
                "engine": "react-flow-webview",
                "workflow_type": "search",
            },
        ],
        "status": "placeholder",
    }


@contract_router.get("/market/agents")
async def list_market_agents_contract():
    return _market_agents_payload()


@contract_router.get("/search")
async def search_contract(q: str = ""):
    return _search_payload(q)


@contract_router.get("/profile/{user_id}")
async def profile_contract(user_id: str):
    return _profile_payload(user_id)


@contract_router.get("/graph/status")
async def graph_status():
    return {
        "status": "blocked",
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "reason": "Neo4j is not available in Cursor Cloud; contract is ready.",
    }


@contract_router.get("/graph/notes")
async def graph_notes(user_id: str | None = None):
    return _knowledge_graph_payload(user_id)


@contract_router.get("/friend-ai/personas")
async def friend_ai_personas():
    return {
        "blocked": True,
        "qdrant_url": settings.qdrant_url,
        "personas": [],
        "reason": "Per-user Qdrant collections are placeholders until middleware is running.",
    }


@contract_router.get("/miniprograms/templates")
async def miniprogram_templates():
    return {
        "templates": [
            {
                "id": "dify-workflow-chat",
                "name": "Dify Workflow 小程序",
                "sandbox": "e2b-placeholder",
            }
        ],
        "status": "placeholder",
    }


@contract_router.get("/canvas/templates")
async def canvas_templates_contract():
    return _canvas_templates_payload()


@contract_router.get("/pdf/dual/templates")
async def dual_pdf_templates():
    return {
        "templates": [
            {
                "id": "dual-pdf-reader",
                "name": "双联 PDF 阅读",
                "engine": "pdf.js",
                "layout": "left-source-right-notes",
            }
        ],
        "status": "placeholder",
    }


@contract_router.get("/commerce/status")
async def commerce_status_contract():
    return _commerce_status_payload()


@contract_router.get("/commerce/cart")
async def commerce_cart():
    return {
        "blocked": True,
        "medusa_api_url": settings.medusa_api_url,
        "items": [],
        "currency": "CNY",
        "total": 0,
    }
