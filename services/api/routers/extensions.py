from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from config import settings

router = APIRouter(prefix="/extensions", tags=["extensions"])
compat_router = APIRouter(tags=["extension-compatibility"])


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


class FriendAIChatRequest(BaseModel):
    message: str
    user_id: str | None = None
    note_collection: str | None = None


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


@router.get("/workflows/templates")
async def workflow_templates():
    return {
        "templates": [
            {
                "id": "research",
                "name": "研究型工作流",
                "nodes": ["search", "draft", "review", "verify"],
            },
            {
                "id": "writing",
                "name": "写作型工作流",
                "nodes": ["outline", "draft", "polish", "proofread"],
            },
            {
                "id": "search",
                "name": "检索型工作流",
                "nodes": ["retrieve", "summarize", "archive"],
            },
        ],
        "engine": "react-flow-webview",
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


async def note_graph(note_id: str):
    return {
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "note_id": note_id,
        "nodes": [{"id": note_id, "label": "note", "type": "note"}],
        "edges": [],
    }


async def friend_ai_chat(friend_id: str, body: FriendAIChatRequest):
    return {
        "blocked": True,
        "friend_id": friend_id,
        "user_id": body.user_id,
        "message": body.message,
        "note_collection": body.note_collection or f"friend-{friend_id}",
        "reason": "Dify and Qdrant are not available in Cursor Cloud; contract is ready.",
    }


@router.post("/mini-programs/generate")
async def generate_mini_program(body: MiniProgramRequest):
    return {
        "status": "placeholder",
        "prompt": body.prompt,
        "dify_workflow_id": body.dify_workflow_id,
        "sandbox": "e2b-placeholder",
    }


async def list_mini_programs():
    return {
        "items": [],
        "generator": "Dify Workflow + e2b sandbox",
        "blocked": not bool(settings.dify_api_key),
    }


@router.get("/canvas/templates")
async def canvas_templates():
    return {
        "templates": [
            {"id": "tldraw-blank", "name": "无限画布", "engine": "tldraw"},
            {"id": "dual-pdf", "name": "双联 PDF 阅读", "engine": "pdf.js"},
        ]
    }


async def dual_pdf_templates():
    return {
        "templates": [
            {
                "id": "dual-pdf-default",
                "name": "双联 PDF 阅读",
                "engine": "pdf.js",
                "panes": ["source-pdf", "notes"],
            }
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


async def desktop_build_plan():
    return {
        "status": "placeholder",
        "targets": ["flutter-desktop", "tauri"],
        "steps": [
            "Install Flutter stable or Tauri toolchain locally.",
            "Run scripts/build-desktop.sh after middleware configuration.",
            "Package artifacts per platform once SDKs are available.",
        ],
    }


@compat_router.get("/openim/status")
async def openim_status_compat():
    return await openim_status()


@compat_router.get("/workflows/templates")
async def workflow_templates_compat():
    return await workflow_templates()


@compat_router.get("/market/agents")
async def list_market_agents_compat():
    return await list_market_agents()


@compat_router.get("/search")
async def search_compat(q: str = ""):
    return await search(q)


@compat_router.get("/profile/{user_id}")
async def profile_compat(user_id: str):
    return await profile(user_id)


@compat_router.get("/graph/notes/{note_id}")
async def note_graph_compat(note_id: str):
    return await note_graph(note_id)


@compat_router.post("/friend-ai/{friend_id}/chat")
async def friend_ai_chat_compat(friend_id: str, body: FriendAIChatRequest):
    return await friend_ai_chat(friend_id, body)


@compat_router.get("/miniprograms")
async def list_mini_programs_compat():
    return await list_mini_programs()


@compat_router.get("/canvas/templates")
async def canvas_templates_compat():
    return await canvas_templates()


@compat_router.get("/dual-pdf/templates")
async def dual_pdf_templates_compat():
    return await dual_pdf_templates()


@compat_router.get("/commerce/status")
async def commerce_status_compat():
    return await commerce_status()


@compat_router.get("/desktop/build-plan")
async def desktop_build_plan_compat():
    return await desktop_build_plan()
