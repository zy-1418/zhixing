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
from models.mini_program import MiniProgram

router = APIRouter(prefix="/mini-programs", tags=["mini-programs"])


class MiniProgramCreate(BaseModel):
    user_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=128)
    prompt: str = Field(..., min_length=1)
    ui_schema: dict[str, Any] = Field(default_factory=dict)


class MiniProgramResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    prompt: str
    dify_workflow_id: str | None
    ui_schema: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=list[MiniProgramResponse])
async def list_mini_programs(
    user_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.scalars(
        select(MiniProgram)
        .where(MiniProgram.user_id == user_id)
        .order_by(MiniProgram.created_at.desc())
    )
    return result.all()


@router.post("", response_model=MiniProgramResponse, status_code=201)
async def create_mini_program(
    body: MiniProgramCreate, db: AsyncSession = Depends(get_db)
):
    program = MiniProgram(**body.model_dump())
    db.add(program)
    await db.commit()
    await db.refresh(program)
    return program


@router.post("/{program_id}/generate-workflow")
async def generate_workflow(program_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    program = await db.get(MiniProgram, program_id)
    if program is None:
        raise HTTPException(status_code=404, detail="Mini program not found")

    if not settings.dify_api_key:
        return {
            "mode": "placeholder",
            "status": "skipped",
            "program_id": str(program.id),
            "reason": "DIFY_API_KEY is not configured in this environment.",
            "workflow_spec": {
                "name": program.name,
                "prompt": program.prompt,
                "ui_schema": program.ui_schema,
            },
        }

    url = f"{settings.dify_api_base_url.rstrip('/')}/workflows"
    headers = {"Authorization": f"Bearer {settings.dify_api_key}"}
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            url,
            headers=headers,
            json={"name": program.name, "description": program.prompt},
        )
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    program.dify_workflow_id = str(data.get("id") or data.get("workflow_id"))
    await db.commit()
    return {"mode": "dify", "program_id": str(program.id), "workflow": data}
