from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from config import settings

router = APIRouter(tags=["future"])


class GraphExtractRequest(BaseModel):
    note_id: uuid.UUID | None = None
    text: str = Field("", max_length=20_000)


class FriendAIChatRequest(BaseModel):
    friend_user_id: uuid.UUID
    message: str = Field(..., min_length=1)


class MiniProgramCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    prompt: str = Field(..., min_length=1, max_length=2000)


class CartItem(BaseModel):
    sku: str
    quantity: int = Field(1, ge=1)


@router.post("/graph/extract")
async def extract_graph(body: GraphExtractRequest):
    entities = []
    if body.text:
        words = [word.strip("，。,. ") for word in body.text.split()]
        entities = [{"id": word, "label": word} for word in words[:8] if word]
    return {
        "mode": "placeholder",
        "neo4j_url": settings.neo4j_url,
        "note_id": str(body.note_id) if body.note_id else None,
        "entities": entities,
        "relations": [],
    }


@router.get("/graph/view")
async def graph_view():
    return {
        "webview": "apps/web/graph/index.html",
        "engine": "sigma.js-placeholder",
        "nodes": [],
        "edges": [],
    }


@router.get("/friend-ai/personas")
async def friend_ai_personas(user_id: uuid.UUID | None = None):
    return {
        "user_id": str(user_id) if user_id else None,
        "qdrant_url": settings.qdrant_url,
        "items": [
            {
                "id": "self-lin",
                "name": "我的林",
                "description": "基于个人笔记的 RAG 分身，占位模式。",
            }
        ],
    }


@router.post("/friend-ai/chat")
async def friend_ai_chat(body: FriendAIChatRequest):
    return {
        "mode": "placeholder",
        "friend_user_id": str(body.friend_user_id),
        "answer": "好友 AI 蒸馏需要 Qdrant 分库与 Dify Workflow；当前返回占位回复。",
    }


@router.post("/mini-programs", status_code=201)
async def create_mini_program(body: MiniProgramCreate):
    return {
        "id": f"mini-{uuid.uuid4().hex[:8]}",
        "name": body.name,
        "prompt": body.prompt,
        "runtime": "dify-workflow+e2b-placeholder",
        "status": "draft",
    }


@router.get("/canvas/templates")
async def canvas_templates():
    return {
        "webview": "apps/web/canvas/index.html",
        "items": [
            {"id": "tldraw-blank", "name": "无限画布"},
            {"id": "mindmap-seed", "name": "观点脑图"},
        ],
    }


@router.get("/pdf/dual-reader")
async def dual_pdf_reader():
    return {
        "webview": "apps/web/pdf_dual/index.html",
        "engine": "pdf.js-placeholder",
        "features": ["left-source", "right-notes", "linked-highlights"],
    }


@router.get("/commerce/wallet")
async def wallet(user_id: uuid.UUID | None = None):
    return {
        "provider": "Medusa",
        "api_url": settings.medusa_api_url,
        "user_id": str(user_id) if user_id else None,
        "balance": 0,
        "currency": "CNY",
        "mode": "placeholder",
    }


@router.post("/commerce/cart/items")
async def add_cart_item(body: CartItem):
    return {
        "provider": "Medusa",
        "mode": "placeholder",
        "item": body.model_dump(),
    }


@router.get("/commerce/orders")
async def orders(user_id: uuid.UUID | None = None):
    return {
        "provider": "Medusa",
        "user_id": str(user_id) if user_id else None,
        "items": [],
        "mode": "placeholder",
    }


@router.get("/desktop/builds")
async def desktop_builds():
    return {
        "target": "flutter-desktop-or-tauri",
        "scripts": ["scripts/build-desktop.ps1"],
        "artifacts": [],
        "mode": "placeholder",
    }


@router.get("/offline/manifest")
async def offline_manifest(user_id: uuid.UUID | None = None):
    return {
        "user_id": str(user_id) if user_id else None,
        "max_cached_notes": 23,
        "items": [],
        "strategy": "recent-notes-first-placeholder",
    }


@router.post("/offline/sync")
async def offline_sync(payload: dict[str, Any]):
    return {
        "accepted": True,
        "mode": "placeholder",
        "received_keys": sorted(payload.keys()),
    }
