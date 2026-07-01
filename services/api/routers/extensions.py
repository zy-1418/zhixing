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


class FriendAISwitchRequest(BaseModel):
    user_id: str
    friend_id: str
    mode: str = Field("rag", description="好友 AI 分身模式，如 rag 或 summary")


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


@router.get("/profile/{user_id}")
async def profile_alias(user_id: str):
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


@router.get("/graph/notes/{note_id}")
async def note_graph(note_id: str):
    return {
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "note_id": note_id,
        "nodes": [{"id": note_id, "label": "note", "type": "note"}],
        "edges": [],
        "reason": "Neo4j is not available in Cursor Cloud; graph contract is ready.",
    }


@router.get("/graph/sigma")
async def sigma_graph_webview():
    return {
        "status": "placeholder",
        "engine": "sigma.js",
        "entry": "apps/mobile/assets/web/sigma/index.html",
        "data_endpoint": "/api/v1/extensions/knowledge/graph",
    }


@router.post("/friend-ai/switch")
async def switch_friend_ai(body: FriendAISwitchRequest):
    return {
        "status": "placeholder",
        "user_id": body.user_id,
        "friend_id": body.friend_id,
        "mode": body.mode,
        "vector_store": "qdrant-user-namespace-placeholder",
        "blocked": True,
        "reason": "Qdrant/Dify are not available in Cursor Cloud.",
    }


@router.post("/mini-programs/generate")
async def generate_mini_program(body: MiniProgramRequest):
    return {
        "status": "placeholder",
        "prompt": body.prompt,
        "dify_workflow_id": body.dify_workflow_id,
        "sandbox": "e2b-placeholder",
    }


@router.get("/miniprograms")
async def list_miniprograms():
    return {
        "status": "placeholder",
        "items": [
            {
                "id": "dify-workflow-starter",
                "name": "Dify Workflow 小程序",
                "engine": "dify-workflow",
                "sandbox": "e2b-placeholder",
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


@router.get("/canvas/templates/tldraw")
async def tldraw_canvas_template():
    return {
        "id": "tldraw-blank",
        "name": "无限画布",
        "engine": "tldraw",
        "webview_entry": "apps/mobile/assets/web/tldraw/index.html",
        "status": "placeholder",
    }


@router.get("/pdf/dual-reader")
async def dual_pdf_reader():
    return {
        "id": "dual-pdf",
        "name": "双联 PDF 阅读",
        "engine": "pdf.js",
        "layout": "source-and-notes",
        "webview_entry": "apps/mobile/assets/web/pdf/dual_reader.html",
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


@router.get("/desktop/builds")
async def desktop_builds():
    return {
        "status": "placeholder",
        "targets": [
            {"id": "linux", "toolchain": "flutter-desktop", "available": False},
            {"id": "macos", "toolchain": "flutter-desktop", "available": False},
            {"id": "windows", "toolchain": "tauri", "available": False},
        ],
        "scripts": ["scripts/build-desktop.sh"],
    }


@router.get("/offline/notes")
async def offline_notes_cache():
    return {
        "status": "placeholder",
        "capacity": 23,
        "strategy": "latest-updated-notes",
        "storage": "flutter-local-cache-placeholder",
    }
