from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.conversation import Conversation
from models.note import Note
from models.task import Task
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


class ConversationCreate(BaseModel):
    user_id: uuid.UUID
    folder_id: Optional[uuid.UUID] = None
    title: str = Field("新对话", max_length=256)
    dify_conversation_id: Optional[str] = Field(None, max_length=128)


class ConversationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    folder_id: Optional[uuid.UUID]
    title: str
    dify_conversation_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


def _folder_node(folder: WorkspaceFolder) -> dict[str, Any]:
    return {
        "id": str(folder.id),
        "name": folder.name,
        "folder_type": folder.folder_type,
        "sort_order": folder.sort_order,
        "children": [],
        "notes": [],
        "tasks": [],
        "conversations": [],
    }


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


@router.get("/tree")
async def workspace_tree(user_id: uuid.UUID = Query(...), db: AsyncSession = Depends(get_db)):
    folders = (
        await db.scalars(
            select(WorkspaceFolder)
            .where(WorkspaceFolder.user_id == user_id)
            .order_by(WorkspaceFolder.sort_order, WorkspaceFolder.created_at)
        )
    ).all()
    notes = (await db.scalars(select(Note).where(Note.user_id == user_id))).all()
    tasks = (await db.scalars(select(Task).where(Task.user_id == user_id))).all()
    conversations = (
        await db.scalars(select(Conversation).where(Conversation.user_id == user_id))
    ).all()

    nodes = {folder.id: _folder_node(folder) for folder in folders}
    roots: list[dict[str, Any]] = []
    for folder in folders:
        node = nodes[folder.id]
        if folder.parent_id and folder.parent_id in nodes:
            nodes[folder.parent_id]["children"].append(node)
        else:
            roots.append(node)

    for note in notes:
        payload = {"id": str(note.id), "title": note.title, "template_type": note.template_type}
        if note.folder_id and note.folder_id in nodes:
            nodes[note.folder_id]["notes"].append(payload)
    for task in tasks:
        payload = {"id": str(task.id), "name": task.name, "status": task.status}
        if task.folder_id and task.folder_id in nodes:
            nodes[task.folder_id]["tasks"].append(payload)
    for conversation in conversations:
        payload = {"id": str(conversation.id), "title": conversation.title}
        if conversation.folder_id and conversation.folder_id in nodes:
            nodes[conversation.folder_id]["conversations"].append(payload)

    return {"items": roots}


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


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    user_id: uuid.UUID = Query(...),
    folder_id: Optional[uuid.UUID] = Query(None),
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
    body: ConversationCreate,
    db: AsyncSession = Depends(get_db),
):
    conversation = Conversation(
        user_id=body.user_id,
        folder_id=body.folder_id,
        title=body.title,
        dify_conversation_id=body.dify_conversation_id,
    )
    db.add(conversation)
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

    payload = {
        "id": str(conversation.id),
        "title": conversation.title,
        "dify_conversation_id": conversation.dify_conversation_id,
        "messages": [],
        "note": "Dify message body is fetched through the Dify proxy when API key is configured.",
    }
    if format == "json":
        return payload

    markdown = [
        f"# {conversation.title}",
        "",
        f"- Conversation ID: `{conversation.id}`",
        f"- Dify ID: `{conversation.dify_conversation_id or '未绑定'}`",
        "",
        "> Dify 自托管/API Key 配置后，此导出端点会补齐消息正文。",
    ]
    return {"content_type": "text/markdown", "content": "\n".join(markdown)}
