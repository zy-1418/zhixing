from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.workspace_folder import WorkspaceFolder

router = APIRouter(prefix="/workspace", tags=["workspace"])

FolderType = Literal["portfolio", "miniapp", "workflow", "skills", "conversation"]


class FolderCreate(BaseModel):
    user_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=256)
    folder_type: FolderType = "portfolio"
    parent_id: Optional[uuid.UUID] = None
    sort_order: int = 0


class FolderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=256)
    folder_type: Optional[FolderType] = None
    parent_id: Optional[uuid.UUID] = None
    sort_order: Optional[int] = None


class FolderResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    parent_id: Optional[uuid.UUID]
    name: str
    folder_type: str
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


@router.get("/folders", response_model=list[FolderResponse])
async def list_folders(
    user_id: uuid.UUID = Query(...),
    parent_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(WorkspaceFolder).where(WorkspaceFolder.user_id == user_id)
    if parent_id is None:
        stmt = stmt.where(WorkspaceFolder.parent_id.is_(None))
    else:
        stmt = stmt.where(WorkspaceFolder.parent_id == parent_id)
    stmt = stmt.order_by(WorkspaceFolder.sort_order, WorkspaceFolder.created_at)
    result = await db.scalars(stmt)
    return result.all()


@router.post("/folders", response_model=FolderResponse, status_code=201)
async def create_folder(body: FolderCreate, db: AsyncSession = Depends(get_db)):
    folder = WorkspaceFolder(
        user_id=body.user_id,
        parent_id=body.parent_id,
        name=body.name,
        folder_type=body.folder_type,
        sort_order=body.sort_order,
    )
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return folder


@router.get("/folders/{folder_id}", response_model=FolderResponse)
async def get_folder(folder_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    folder = await db.get(WorkspaceFolder, folder_id)
    if folder is None:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder


@router.patch("/folders/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: uuid.UUID,
    body: FolderUpdate,
    db: AsyncSession = Depends(get_db),
):
    folder = await db.get(WorkspaceFolder, folder_id)
    if folder is None:
        raise HTTPException(status_code=404, detail="Folder not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(folder, field, value)

    await db.commit()
    await db.refresh(folder)
    return folder


@router.delete("/folders/{folder_id}", status_code=204)
async def delete_folder(folder_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    folder = await db.get(WorkspaceFolder, folder_id)
    if folder is None:
        raise HTTPException(status_code=404, detail="Folder not found")
    await db.delete(folder)
    await db.commit()
