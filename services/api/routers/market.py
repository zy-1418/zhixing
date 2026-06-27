from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from models.agent_tool import AgentTool

router = APIRouter(prefix="/market", tags=["market"])


class AgentToolCreate(BaseModel):
    provider: str = "dify"
    external_id: str | None = Field(None, max_length=128)
    name: str = Field(..., min_length=1, max_length=128)
    description: str = ""
    tool_schema: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class AgentToolResponse(BaseModel):
    id: uuid.UUID
    provider: str
    external_id: str | None
    name: str
    description: str
    tool_schema: dict
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


@router.get("/agents", response_model=list[AgentToolResponse])
async def list_agents(db: AsyncSession = Depends(get_db)):
    result = await db.scalars(
        select(AgentTool).where(AgentTool.enabled.is_(True)).order_by(AgentTool.name)
    )
    return result.all()


@router.post("/agents", response_model=AgentToolResponse, status_code=201)
async def create_agent_tool(
    body: AgentToolCreate, db: AsyncSession = Depends(get_db)
):
    tool = AgentTool(**body.model_dump())
    db.add(tool)
    await db.commit()
    await db.refresh(tool)
    return tool


@router.post("/sync/dify")
async def sync_dify_tools(db: AsyncSession = Depends(get_db)):
    if not settings.dify_api_key:
        return {
            "mode": "placeholder",
            "provider": "dify",
            "status": "skipped",
            "reason": "DIFY_API_KEY is not configured in this environment.",
            "synced": 0,
        }

    url = f"{settings.dify_api_base_url.rstrip('/')}/tools"
    headers = {"Authorization": f"Bearer {settings.dify_api_key}"}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url, headers=headers)
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    items = data if isinstance(data, list) else data.get("data", [])
    synced = 0
    for item in items:
        external_id = str(item.get("id") or item.get("name"))
        existing = await db.scalar(
            select(AgentTool).where(
                AgentTool.provider == "dify", AgentTool.external_id == external_id
            )
        )
        payload = {
            "provider": "dify",
            "external_id": external_id,
            "name": item.get("name") or external_id,
            "description": item.get("description") or "",
            "tool_schema": item,
            "enabled": True,
        }
        if existing is None:
            db.add(AgentTool(**payload))
        else:
            for field, value in payload.items():
                setattr(existing, field, value)
        synced += 1

    await db.commit()
    return {"provider": "dify", "synced": synced}
