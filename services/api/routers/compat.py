from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from config import settings

router = APIRouter(tags=["compatibility"])


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
async def openim_status_alias():
    return {
        "service": "OpenIM",
        "status": "placeholder",
        "docs": "docs/OPENIM.md",
        "capabilities": ["friends", "groups", "team-chat"],
    }


@router.post("/workflows")
async def save_workflow_alias(definition: WorkflowDefinition):
    return {
        "status": "saved-placeholder",
        "engine": "react-flow-webview",
        "definition": definition.model_dump(),
    }


@router.get("/workflows/templates")
async def workflow_templates():
    return {
        "templates": [
            {
                "id": "research-sop",
                "name": "Research SOP",
                "nodes": ["search", "draft", "review", "verify"],
            },
            {
                "id": "writing-sop",
                "name": "Writing SOP",
                "nodes": ["outline", "draft", "polish", "proofread"],
            },
        ]
    }


@router.get("/market/agents")
async def list_market_agents_alias():
    return {
        "blocked": not bool(settings.dify_api_key),
        "source": "Dify tools marketplace",
        "items": [
            {
                "id": "lin",
                "name": "Lin",
                "description": "Zhixing MVP default chat/RAG agent placeholder.",
                "enabled": bool(settings.dify_api_key),
            }
        ],
    }


@router.post("/search/index")
async def index_documents_alias(body: SearchIndexRequest):
    return {
        "status": "accepted-placeholder",
        "meili_url": settings.meili_url,
        "collection": body.collection,
        "count": len(body.documents),
    }


@router.get("/search")
async def search_alias(q: str):
    return {
        "query": q,
        "blocked": True,
        "reason": "Meilisearch is not available in Cursor Cloud; contract is ready.",
        "items": [],
    }


@router.get("/profile/{user_id}")
async def profile_alias(user_id: str):
    return {
        "user_id": user_id,
        "works": [],
        "likes": [],
        "collections": [],
        "tags": [],
        "status": "placeholder",
    }


@router.get("/profiles/{user_id}")
async def profiles_alias(user_id: str):
    return await profile_alias(user_id)


@router.get("/knowledge/graph")
async def knowledge_graph_alias(user_id: str | None = None):
    return {
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "user_id": user_id,
        "nodes": [],
        "edges": [],
    }


@router.get("/graph")
async def graph_alias(user_id: str | None = None):
    return await knowledge_graph_alias(user_id)


@router.get("/friend-ai/status")
async def friend_ai_status():
    return {
        "blocked": True,
        "qdrant_url": settings.qdrant_url,
        "mode": "per-user-rag-placeholder",
    }


@router.get("/friend-ai/{user_id}")
async def friend_ai_profile(user_id: str):
    return {
        "user_id": user_id,
        "blocked": True,
        "collections": [],
        "reason": "Qdrant is not available in Cursor Cloud.",
    }


@router.post("/miniprograms/generate")
async def generate_miniprogram_alias(body: MiniProgramRequest):
    return {
        "status": "placeholder",
        "prompt": body.prompt,
        "dify_workflow_id": body.dify_workflow_id,
        "sandbox": "e2b-placeholder",
    }


@router.post("/mini-programs/generate")
async def generate_mini_program_alias(body: MiniProgramRequest):
    return await generate_miniprogram_alias(body)


@router.get("/canvas/templates")
async def canvas_templates_alias():
    return {
        "templates": [
            {"id": "tldraw-blank", "name": "Infinite canvas", "engine": "tldraw"},
            {"id": "dual-pdf", "name": "Dual PDF reader", "engine": "pdf.js"},
        ]
    }


@router.get("/dual-pdf/templates")
async def dual_pdf_templates():
    return {
        "templates": [
            {
                "id": "dual-pdf-default",
                "name": "Dual PDF reader",
                "engine": "pdf.js",
            }
        ]
    }


@router.get("/commerce/status")
async def commerce_status_alias():
    return {
        "blocked": True,
        "medusa_api_url": settings.medusa_api_url,
        "capabilities": ["orders", "cart", "wallet"],
    }


@router.get("/desktop/status")
async def desktop_status_alias():
    return {
        "status": "placeholder",
        "targets": ["flutter-desktop", "tauri"],
        "scripts": ["scripts/build-desktop.sh"],
    }


@router.get("/desktop/builds")
async def desktop_builds():
    return {
        "status": "placeholder",
        "builds": [],
        "targets": ["linux", "macos", "windows"],
        "script": "scripts/build-desktop.sh",
    }
