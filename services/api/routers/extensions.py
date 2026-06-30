from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from config import settings

router = APIRouter(prefix="/extensions", tags=["extensions"])
root_router = APIRouter(tags=["extensions"])


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


@root_router.get("/openim/status")
async def openim_status_alias():
    return await openim_status()


@root_router.post("/workflows")
async def save_workflow_alias(definition: WorkflowDefinition):
    return await save_workflow(definition)


@root_router.get("/workflows/templates")
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


@root_router.get("/market/agents")
async def list_market_agents_alias():
    return await list_market_agents()


@root_router.post("/search/index")
async def index_documents_alias(body: SearchIndexRequest):
    return await index_documents(body)


@root_router.get("/search")
async def search_alias(q: str):
    return await search(q)


@root_router.get("/profile/{user_id}")
async def profile_alias(user_id: str):
    return await profile(user_id)


@root_router.get("/graph/notes/{note_id}")
async def note_graph(note_id: str):
    graph = await knowledge_graph(user_id=None)
    return {
        **graph,
        "note_id": note_id,
        "pipeline": "neo4j-note-relation-placeholder",
    }


@root_router.get("/friend-ai/personas")
async def friend_ai_personas(user_id: str | None = None):
    return {
        "blocked": True,
        "qdrant_url": settings.qdrant_url,
        "user_id": user_id,
        "personas": [],
        "reason": "Qdrant/Dify are unavailable in Cursor Cloud; contract is ready.",
    }


@root_router.post("/friend-ai/chat")
async def friend_ai_chat(payload: dict[str, Any]):
    return {
        "blocked": True,
        "persona_id": payload.get("persona_id"),
        "echo": payload.get("message"),
        "reason": "Friend AI RAG requires Dify and Qdrant.",
    }


@root_router.get("/miniprograms")
async def list_miniprograms():
    return {
        "items": [],
        "sandbox": "e2b-placeholder",
        "dify_configured": bool(settings.dify_api_key),
    }


@root_router.post("/miniprograms")
async def generate_miniprogram_alias(body: MiniProgramRequest):
    return await generate_mini_program(body)


@root_router.get("/canvas/templates")
async def canvas_templates_alias():
    return await canvas_templates()


@root_router.get("/dual-pdf/templates")
async def dual_pdf_templates():
    return {
        "templates": [
            {
                "id": "dual-pdf-reader",
                "name": "双联 PDF 阅读",
                "engine": "pdf.js",
                "panes": ["source", "notes"],
            }
        ]
    }


@root_router.get("/commerce/status")
async def commerce_status_alias():
    return await commerce_status()


@root_router.get("/commerce/cart")
async def cart_status():
    return {
        "blocked": True,
        "medusa_api_url": settings.medusa_api_url,
        "items": [],
    }


@root_router.get("/desktop/status")
async def desktop_status_alias():
    return await desktop_status()
