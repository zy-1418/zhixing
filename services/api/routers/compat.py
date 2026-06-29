from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from models.conversation import Conversation

router = APIRouter(tags=["compatibility"])


class DebateCreate(BaseModel):
    post_id: str | None = None
    topic: str = Field(..., min_length=1, max_length=240)
    summary: str = ""


class CartItem(BaseModel):
    sku: str = Field(..., min_length=1)
    quantity: int = Field(1, ge=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


_debates: dict[str, dict[str, Any]] = {}
_cart_items: list[dict[str, Any]] = []


def _now() -> str:
    return datetime.now(UTC).isoformat()


async def _export_conversation_response(
    conversation_id: uuid.UUID,
    export_format: Literal["json", "markdown"],
    db: AsyncSession,
) -> Response:
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if export_format == "json":
        return Response(
            json.dumps(
                {
                    "id": str(conversation.id),
                    "title": conversation.title,
                    "messages": conversation.messages,
                },
                ensure_ascii=False,
                indent=2,
            ),
            media_type="application/json",
        )

    lines = [f"# {conversation.title}", ""]
    for message in conversation.messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        lines.extend([f"## {role}", "", str(content), ""])
    return Response("\n".join(lines), media_type="text/markdown; charset=utf-8")


@router.get("/conversations/{conversation_id}/export.json")
async def export_conversation_json(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await _export_conversation_response(conversation_id, "json", db)


@router.get("/conversations/{conversation_id}/export.md")
async def export_conversation_markdown(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await _export_conversation_response(conversation_id, "markdown", db)


@router.get("/debates")
async def list_debates():
    return sorted(_debates.values(), key=lambda item: item["created_at"], reverse=True)


@router.post("/debates", status_code=201)
async def create_debate(body: DebateCreate):
    debate_id = str(uuid.uuid4())
    debate = {
        "id": debate_id,
        "post_id": body.post_id,
        "topic": body.topic,
        "summary": body.summary,
        "comments": [],
        "created_at": _now(),
        "status": "placeholder",
    }
    _debates[debate_id] = debate
    return debate


@router.get("/workflows/templates")
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


@router.get("/market/agents")
async def market_agents():
    return {
        "blocked": not bool(settings.dify_api_key),
        "source": "Dify tools marketplace",
        "items": [
            {
                "id": "lin",
                "name": "林",
                "description": "知行默认对话/RAG Agent，占位同步 Dify 工具。",
                "enabled": bool(settings.dify_api_key),
            }
        ],
    }


@router.get("/search")
async def root_search(q: str = Query("", description="搜索关键词")):
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


@router.get("/graph/status")
async def graph_status():
    return {
        "blocked": True,
        "neo4j_url": settings.neo4j_url,
        "pipeline": "note-relation-extractor-placeholder",
        "nodes_indexed": 0,
    }


@router.get("/friend-ai/personas")
async def friend_ai_personas(user_id: str | None = None):
    return {
        "blocked": True,
        "qdrant_url": settings.qdrant_url,
        "user_id": user_id,
        "personas": [],
        "reason": "Qdrant and Dify are unavailable in Cursor Cloud.",
    }


@router.get("/miniprograms/templates")
async def mini_program_templates():
    return {
        "sandbox": "e2b-placeholder",
        "templates": [
            {
                "id": "dify-workflow-chat",
                "name": "Dify Workflow 小程序",
                "inputs": ["prompt", "files"],
            }
        ],
    }


@router.get("/canvas/templates")
async def root_canvas_templates():
    return {
        "templates": [
            {"id": "tldraw-blank", "name": "无限画布", "engine": "tldraw"},
            {"id": "mindmap", "name": "脑图草稿", "engine": "tldraw"},
        ]
    }


@router.get("/pdf/dual/templates")
async def dual_pdf_templates():
    return {
        "templates": [
            {
                "id": "dual-column-reader",
                "name": "双联 PDF 阅读",
                "engine": "pdf.js",
                "panes": ["source", "notes"],
            }
        ]
    }


@router.get("/commerce/status")
async def root_commerce_status():
    return {
        "blocked": True,
        "medusa_api_url": settings.medusa_api_url,
        "capabilities": ["orders", "cart", "wallet"],
    }


@router.get("/commerce/cart")
async def get_cart():
    return {
        "blocked": True,
        "medusa_api_url": settings.medusa_api_url,
        "items": _cart_items,
        "reason": "Medusa is not available in Cursor Cloud; cart contract is ready.",
    }


@router.post("/commerce/cart", status_code=202)
async def add_cart_item(item: CartItem):
    cart_item = {
        "id": str(uuid.uuid4()),
        "sku": item.sku,
        "quantity": item.quantity,
        "metadata": item.metadata,
        "created_at": _now(),
    }
    _cart_items.append(cart_item)
    return {
        "blocked": True,
        "medusa_api_url": settings.medusa_api_url,
        "item": cart_item,
    }
