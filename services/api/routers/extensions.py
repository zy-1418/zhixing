from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from config import settings

router = APIRouter(prefix="/extensions", tags=["extensions"])
compat_router = APIRouter(tags=["extensions"])


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


async def openim_status():
    return {
        "service": "OpenIM",
        "status": "placeholder",
        "docs": "docs/OPENIM.md",
        "capabilities": ["friends", "groups", "team-chat"],
    }


async def save_workflow(definition: WorkflowDefinition):
    return {
        "status": "saved-placeholder",
        "engine": "react-flow-webview",
        "definition": definition.model_dump(),
    }


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


async def index_documents(body: SearchIndexRequest):
    return {
        "status": "accepted-placeholder",
        "meili_url": settings.meili_url,
        "collection": body.collection,
        "count": len(body.documents),
    }


async def search(q: str):
    return {
        "query": q,
        "blocked": True,
        "reason": "Meilisearch is not available in Cursor Cloud; contract is ready.",
        "items": [],
    }


async def profile(user_id: str):
    return {
        "user_id": user_id,
        "works": [],
        "likes": [],
        "collections": [],
        "tags": [],
        "status": "placeholder",
    }


async def knowledge_graph(user_id: str | None = None):
    return {
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "user_id": user_id,
        "nodes": [],
        "edges": [],
    }


async def generate_mini_program(body: MiniProgramRequest):
    return {
        "status": "placeholder",
        "prompt": body.prompt,
        "dify_workflow_id": body.dify_workflow_id,
        "sandbox": "e2b-placeholder",
    }


async def canvas_templates():
    return {
        "templates": [
            {"id": "tldraw-blank", "name": "无限画布", "engine": "tldraw"},
            {"id": "dual-pdf", "name": "双联 PDF 阅读", "engine": "pdf.js"},
        ]
    }


async def commerce_status():
    return {
        "blocked": True,
        "medusa_api_url": settings.medusa_api_url,
        "capabilities": ["orders", "cart", "wallet"],
    }


async def desktop_status():
    return {
        "status": "placeholder",
        "targets": ["flutter-desktop", "tauri"],
        "scripts": ["scripts/build-desktop.sh"],
    }


async def workflow_templates():
    return {
        "engine": "react-flow-webview",
        "templates": [
            {
                "id": "research-sop",
                "name": "研究型 SOP",
                "nodes": ["input", "dify-rag", "metagpt-sop", "workspace-export"],
            },
            {
                "id": "writing-sop",
                "name": "写作型 SOP",
                "nodes": ["outline", "draft", "polish", "review"],
            },
        ],
    }


async def note_graph(note_id: str):
    return {
        "note_id": note_id,
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "nodes": [],
        "edges": [],
        "reason": "Neo4j is not available in Cursor Cloud; graph API contract is ready.",
    }


async def friend_ai(user_id: str):
    return {
        "user_id": user_id,
        "blocked": True,
        "qdrant_url": settings.qdrant_url,
        "collections": [f"friend_ai_{user_id}"],
        "reason": "Per-user RAG collections require Qdrant and Dify runtime.",
    }


async def list_mini_programs():
    return {
        "blocked": not bool(settings.dify_api_key),
        "sandbox": "e2b-placeholder",
        "items": [],
    }


async def dual_pdf_templates():
    return {
        "templates": [
            {
                "id": "dual-pdf-default",
                "name": "双联 PDF 阅读",
                "engine": "pdf.js",
                "panes": ["source", "notes"],
            }
        ]
    }


async def cart_status():
    return {
        "blocked": True,
        "medusa_api_url": settings.medusa_api_url,
        "items": [],
        "currency": "CNY",
    }


router.add_api_route("/openim/status", openim_status, methods=["GET"])
router.add_api_route("/workflows", save_workflow, methods=["POST"])
router.add_api_route("/workflows/templates", workflow_templates, methods=["GET"])
router.add_api_route("/market/agents", list_market_agents, methods=["GET"])
router.add_api_route("/search/index", index_documents, methods=["POST"])
router.add_api_route("/search", search, methods=["GET"])
router.add_api_route("/profiles/{user_id}", profile, methods=["GET"])
router.add_api_route("/profile/{user_id}", profile, methods=["GET"])
router.add_api_route("/knowledge/graph", knowledge_graph, methods=["GET"])
router.add_api_route("/graph/notes/{note_id}", note_graph, methods=["GET"])
router.add_api_route("/friend-ai/{user_id}", friend_ai, methods=["GET"])
router.add_api_route("/mini-programs/generate", generate_mini_program, methods=["POST"])
router.add_api_route("/miniprograms", list_mini_programs, methods=["GET"])
router.add_api_route("/canvas/templates", canvas_templates, methods=["GET"])
router.add_api_route("/dual-pdf/templates", dual_pdf_templates, methods=["GET"])
router.add_api_route("/commerce/status", commerce_status, methods=["GET"])
router.add_api_route("/cart", cart_status, methods=["GET"])
router.add_api_route("/desktop/status", desktop_status, methods=["GET"])

compat_router.add_api_route("/openim/status", openim_status, methods=["GET"])
compat_router.add_api_route("/workflows/templates", workflow_templates, methods=["GET"])
compat_router.add_api_route("/market/agents", list_market_agents, methods=["GET"])
compat_router.add_api_route("/search", search, methods=["GET"])
compat_router.add_api_route("/profile/{user_id}", profile, methods=["GET"])
compat_router.add_api_route("/graph/notes/{note_id}", note_graph, methods=["GET"])
compat_router.add_api_route("/friend-ai/{user_id}", friend_ai, methods=["GET"])
compat_router.add_api_route("/miniprograms", list_mini_programs, methods=["GET"])
compat_router.add_api_route("/canvas/templates", canvas_templates, methods=["GET"])
compat_router.add_api_route("/dual-pdf/templates", dual_pdf_templates, methods=["GET"])
compat_router.add_api_route("/commerce/status", commerce_status, methods=["GET"])
compat_router.add_api_route("/cart", cart_status, methods=["GET"])
compat_router.add_api_route("/desktop/status", desktop_status, methods=["GET"])
