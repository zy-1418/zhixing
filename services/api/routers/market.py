from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/market", tags=["market"])

_agents: dict[str, dict] = {
    "lin": {
        "id": "lin",
        "name": "林",
        "source": "dify",
        "description": "知行默认学习、研究、写作助手。",
        "tags": ["chat", "rag", "writing"],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
}


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    source: str = "dify"
    description: str = ""
    tags: list[str] = Field(default_factory=list)


@router.get("/agents")
async def list_agents():
    return list(_agents.values())


@router.post("/agents/sync")
async def sync_dify_agents():
    return {
        "status": "placeholder",
        "detail": "Dify tool sync requires DIFY_API_KEY in a self-hosted or cloud Dify environment.",
        "items": list(_agents.values()),
    }


@router.post("/agents", status_code=201)
async def create_agent(body: AgentCreate):
    agent_id = str(uuid.uuid4())
    agent = {
        "id": agent_id,
        **body.model_dump(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _agents[agent_id] = agent
    return agent
