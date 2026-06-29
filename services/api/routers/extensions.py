from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from config import settings

router = APIRouter(prefix="/extensions", tags=["extensions"])
contract_router = APIRouter(tags=["extension-contracts"])


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


@contract_router.get("/openim/status")
async def openim_status_contract():
    return await openim_status()


@router.post("/workflows")
async def save_workflow(definition: WorkflowDefinition):
    return {
        "status": "saved-placeholder",
        "engine": "react-flow-webview",
        "definition": definition.model_dump(),
    }


@contract_router.get("/workflows/templates")
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
                "nodes": ["outline", "draft", "polish", "proofread"],
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


@contract_router.get("/market/agents")
async def list_market_agents_contract():
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


@contract_router.get("/search")
async def search_contract(q: str):
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


@contract_router.get("/profile/{user_id}")
async def profile_contract(user_id: str):
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


@contract_router.get("/graph/status")
async def graph_status():
    return {
        "status": "placeholder",
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "pipeline": "note-relation-extraction",
    }


@contract_router.get("/friend-ai/personas")
async def friend_ai_personas(user_id: str | None = None):
    return {
        "blocked": True,
        "reason": "Qdrant/Dify is not available in Cursor Cloud; contract is ready.",
        "qdrant_url": settings.qdrant_url,
        "user_id": user_id,
        "personas": [],
    }


@router.post("/mini-programs/generate")
async def generate_mini_program(body: MiniProgramRequest):
    return {
        "status": "placeholder",
        "prompt": body.prompt,
        "dify_workflow_id": body.dify_workflow_id,
        "sandbox": "e2b-placeholder",
    }


@contract_router.get("/miniprograms/templates")
async def miniprogram_templates():
    return {
        "runtime": "dify-workflow-e2b-placeholder",
        "templates": [
            {
                "id": "qa-tool",
                "name": "问答小程序",
                "description": "Dify Workflow 输入输出占位模板。",
            }
        ],
    }


@router.get("/canvas/templates")
async def canvas_templates():
    return {
        "templates": [
            {"id": "tldraw-blank", "name": "无限画布", "engine": "tldraw"},
            {"id": "dual-pdf", "name": "双联 PDF 阅读", "engine": "pdf.js"},
        ]
    }


@contract_router.get("/canvas/templates")
async def canvas_templates_contract():
    return await canvas_templates()


@contract_router.get("/dual-pdf/templates")
async def dual_pdf_templates():
    return {
        "engine": "pdf.js",
        "templates": [
            {
                "id": "dual-pdf-default",
                "name": "双联 PDF 阅读",
                "panes": ["source", "notes"],
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


@contract_router.get("/commerce/status")
async def commerce_status_contract():
    return await commerce_status()


@contract_router.get("/commerce/cart")
async def commerce_cart(user_id: str | None = None):
    return {
        "blocked": True,
        "medusa_api_url": settings.medusa_api_url,
        "user_id": user_id,
        "items": [],
        "wallet": {"balance": 0, "currency": "CNY"},
    }


@router.get("/desktop/status")
async def desktop_status():
    return {
        "status": "placeholder",
        "targets": ["flutter-desktop", "tauri"],
        "scripts": ["scripts/build-desktop.sh"],
    }


@contract_router.get("/desktop/status")
async def desktop_status_contract():
    return await desktop_status()
