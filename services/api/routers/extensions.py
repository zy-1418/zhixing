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


class CartItemRequest(BaseModel):
    product_id: str
    quantity: int = Field(1, ge=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


@router.get("/openim/status")
async def openim_status():
    return {
        "service": "OpenIM",
        "status": "placeholder",
        "docs": "docs/OPENIM.md",
        "capabilities": ["friends", "groups", "team-chat"],
    }


@compat_router.get("/openim/status")
async def openim_status_compat():
    return await openim_status()


@router.post("/workflows")
async def save_workflow(definition: WorkflowDefinition):
    return {
        "status": "saved-placeholder",
        "engine": "react-flow-webview",
        "definition": definition.model_dump(),
    }


@compat_router.get("/workflows/templates")
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


@compat_router.get("/market/agents")
async def list_market_agents_compat():
    return await list_market_agents()


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


@compat_router.get("/search")
async def search_compat(q: str):
    return await search(q)


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


@compat_router.get("/profile/{user_id}")
async def profile_compat(user_id: str):
    return await profile(user_id)


@router.get("/knowledge/graph")
async def knowledge_graph(user_id: str | None = None):
    return {
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "user_id": user_id,
        "nodes": [],
        "edges": [],
    }


@compat_router.get("/graph/status")
async def graph_status(user_id: str | None = None):
    graph = await knowledge_graph(user_id=user_id)
    return {
        "status": "placeholder",
        "blocked": graph["blocked"],
        "neo4j_url": graph["neo4j_url"],
        "user_id": graph["user_id"],
    }


@compat_router.get("/friend-ai/personas")
async def friend_ai_personas(user_id: str | None = None):
    return {
        "blocked": True,
        "qdrant_url": settings.qdrant_url,
        "user_id": user_id,
        "personas": [],
        "reason": "Qdrant/Dify are not available in Cursor Cloud; contract is ready.",
    }


@router.post("/mini-programs/generate")
async def generate_mini_program(body: MiniProgramRequest):
    return {
        "status": "placeholder",
        "prompt": body.prompt,
        "dify_workflow_id": body.dify_workflow_id,
        "sandbox": "e2b-placeholder",
    }


@compat_router.get("/miniprograms/templates")
async def miniprogram_templates():
    return {
        "templates": [
            {
                "id": "dify-workflow-chat",
                "name": "Dify Workflow 小程序",
                "sandbox": "e2b-placeholder",
            }
        ]
    }


@router.get("/canvas/templates")
async def canvas_templates():
    return {
        "templates": [
            {"id": "tldraw-blank", "name": "无限画布", "engine": "tldraw"},
            {"id": "dual-pdf", "name": "双联 PDF 阅读", "engine": "pdf.js"},
        ]
    }


@compat_router.get("/canvas/templates")
async def canvas_templates_compat():
    return await canvas_templates()


@compat_router.get("/dual-pdf/templates")
async def dual_pdf_templates():
    return {
        "templates": [
            {"id": "dual-pdf", "name": "双联 PDF 阅读", "engine": "pdf.js"}
        ]
    }


@router.get("/commerce/status")
async def commerce_status():
    return {
        "blocked": True,
        "medusa_api_url": settings.medusa_api_url,
        "capabilities": ["orders", "cart", "wallet"],
    }


@compat_router.get("/commerce/status")
async def commerce_status_compat():
    return await commerce_status()


@compat_router.get("/cart/items")
async def list_cart_items(user_id: str | None = None):
    return {
        "blocked": True,
        "medusa_api_url": settings.medusa_api_url,
        "user_id": user_id,
        "items": [],
    }


@compat_router.post("/cart/items", status_code=201)
async def add_cart_item(body: CartItemRequest):
    return {
        "blocked": True,
        "medusa_api_url": settings.medusa_api_url,
        "item": body.model_dump(),
    }


@router.get("/desktop/status")
async def desktop_status():
    return {
        "status": "placeholder",
        "targets": ["flutter-desktop", "tauri"],
        "scripts": ["scripts/build-desktop.sh"],
    }


@compat_router.get("/desktop/status")
async def desktop_status_compat():
    return await desktop_status()
