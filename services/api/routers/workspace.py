from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.conversation import Conversation
from models.workspace_folder import WorkspaceFolder

router = APIRouter(prefix="/workspace", tags=["workspace"])
compat_router = APIRouter(tags=["workspace-compat"])

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


class ConversationCreate(BaseModel):
    user_id: uuid.UUID
    folder_id: uuid.UUID | None = None
    title: str = Field("新对话", min_length=1, max_length=256)
    dify_conversation_id: str | None = None
    messages: list[dict[str, Any]] = Field(default_factory=list)


class ConversationUpdate(BaseModel):
    folder_id: uuid.UUID | None = None
    title: str | None = Field(None, min_length=1, max_length=256)
    dify_conversation_id: str | None = None
    messages: list[dict[str, Any]] | None = None


class ConversationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    folder_id: uuid.UUID | None
    title: str
    dify_conversation_id: str | None
    messages: list[dict[str, Any]]
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


@router.get("/tree")
async def folder_tree(user_id: uuid.UUID = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.scalars(
        select(WorkspaceFolder)
        .where(WorkspaceFolder.user_id == user_id)
        .order_by(WorkspaceFolder.sort_order, WorkspaceFolder.created_at)
    )
    folders = result.all()
    nodes = {
        str(folder.id): {
            "id": str(folder.id),
            "parent_id": str(folder.parent_id) if folder.parent_id else None,
            "name": folder.name,
            "folder_type": folder.folder_type,
            "sort_order": folder.sort_order,
            "children": [],
        }
        for folder in folders
    }
    roots = []
    for folder in folders:
        node = nodes[str(folder.id)]
        if folder.parent_id and str(folder.parent_id) in nodes:
            nodes[str(folder.parent_id)]["children"].append(node)
        else:
            roots.append(node)
    return roots


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    user_id: uuid.UUID = Query(...),
    folder_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Conversation).where(Conversation.user_id == user_id)
    if folder_id is not None:
        stmt = stmt.where(Conversation.folder_id == folder_id)
    stmt = stmt.order_by(Conversation.updated_at.desc())
    result = await db.scalars(stmt)
    return result.all()


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    body: ConversationCreate, db: AsyncSession = Depends(get_db)
):
    conversation = Conversation(
        user_id=body.user_id,
        folder_id=body.folder_id,
        title=body.title,
        dify_conversation_id=body.dify_conversation_id,
        messages=body.messages,
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: uuid.UUID,
    body: ConversationUpdate,
    db: AsyncSession = Depends(get_db),
):
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(conversation, field, value)
    await db.commit()
    await db.refresh(conversation)
    return conversation


@router.get("/conversations/{conversation_id}/export")
async def export_conversation(
    conversation_id: uuid.UUID,
    format: Literal["json", "markdown"] = Query("markdown"),
    db: AsyncSession = Depends(get_db),
):
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if format == "json":
        import json

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


@compat_router.get("/conversations/{conversation_id}/export")
async def export_conversation_alias(
    conversation_id: uuid.UUID,
    format: Literal["json", "markdown"] = Query("markdown"),
    db: AsyncSession = Depends(get_db),
):
    return await export_conversation(conversation_id, format, db)


@compat_router.get("/conversations/{conversation_id}/export.json")
async def export_conversation_json_alias(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await export_conversation(conversation_id, "json", db)


@compat_router.get("/conversations/{conversation_id}/export.md")
async def export_conversation_markdown_alias(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await export_conversation(conversation_id, "markdown", db)
