from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from config import settings
from routers.extensions import (
    MiniProgramRequest,
    WorkflowDefinition,
    canvas_templates,
    commerce_status,
    list_market_agents,
    openim_status,
    save_workflow,
    search,
)
from routers.social import DebateCreate, create_debate

router = APIRouter(tags=["compat"])


@router.get("/openim/status")
async def openim_status_compat():
    return await openim_status()


@router.post("/debates", status_code=201)
async def create_debate_compat(body: DebateCreate):
    return await create_debate(body)


@router.get("/workflows")
async def list_workflows_compat():
    return {
        "status": "placeholder",
        "engine": "react-flow-webview",
        "items": [],
    }


@router.post("/workflows")
async def save_workflow_compat(definition: WorkflowDefinition):
    return await save_workflow(definition)


@router.get("/market/agents")
async def list_market_agents_compat():
    return await list_market_agents()


@router.get("/search")
async def search_compat(q: str = Query("")):
    return await search(q)


@router.get("/profile/{user_id}")
async def profile_compat(user_id: str):
    return {
        "user_id": user_id,
        "works": [],
        "likes": [],
        "collections": [],
        "tags": [],
        "offline_cache": {"note_limit": 23, "status": "placeholder"},
        "status": "placeholder",
    }


@router.get("/graph/notes/{note_id}")
async def note_graph_compat(note_id: str):
    return {
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "note_id": note_id,
        "nodes": [],
        "edges": [],
    }


@router.get("/friend-ai/profiles")
async def friend_ai_profiles_compat(user_id: str | None = Query(None)):
    return {
        "blocked": True,
        "qdrant_url": settings.qdrant_url,
        "user_id": user_id,
        "profiles": [],
        "strategy": "per-user-rag-collection-placeholder",
    }


@router.get("/miniprograms")
async def list_miniprograms_compat():
    return {
        "status": "placeholder",
        "items": [],
        "workflow_engine": "dify-workflow",
        "sandbox": "e2b-placeholder",
    }


@router.post("/miniprograms")
async def create_miniprogram_compat(body: MiniProgramRequest):
    return {
        "status": "placeholder",
        "prompt": body.prompt,
        "dify_workflow_id": body.dify_workflow_id,
        "inputs": body.inputs,
        "sandbox": "e2b-placeholder",
    }


@router.get("/canvas/templates")
async def canvas_templates_compat():
    return await canvas_templates()


@router.get("/dual-pdf/templates")
async def dual_pdf_templates_compat():
    return {
        "templates": [
            {
                "id": "dual-pdf-default",
                "name": "Dual PDF reader",
                "engine": "pdf.js",
                "layout": "two-pane",
            }
        ]
    }


@router.get("/commerce/status")
async def commerce_status_compat():
    return await commerce_status()


@router.get("/desktop/builds")
async def desktop_builds_compat():
    return {
        "status": "placeholder",
        "targets": ["flutter-desktop", "tauri"],
        "scripts": ["scripts/build-desktop.sh"],
        "artifacts": [],
    }


@router.post("/search/index")
async def index_documents_compat(body: dict[str, Any]):
    return {
        "status": "accepted-placeholder",
        "meili_url": settings.meili_url,
        "collection": body.get("collection", "default"),
        "count": len(body.get("documents", [])),
    }
