from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.conversation import Conversation
from models.workspace_folder import WorkspaceFolder

router = APIRouter(prefix="/workspace", tags=["workspace"])

FolderType = Literal["portfolio", "miniapp", "workflow", "skills", "conversation"]
ExportFormat = Literal["json", "markdown"]


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


class FolderTreeNode(FolderResponse):
    children: list["FolderTreeNode"] = Field(default_factory=list)


class ConversationCreate(BaseModel):
    user_id: uuid.UUID
    title: str = Field("新对话", min_length=1, max_length=256)
    folder_id: Optional[uuid.UUID] = None
    dify_conversation_id: Optional[str] = Field(None, max_length=128)


class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=256)
    folder_id: Optional[uuid.UUID] = None
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


def _folder_node(folder: WorkspaceFolder) -> dict:
    return {
        "id": folder.id,
        "user_id": folder.user_id,
        "parent_id": folder.parent_id,
        "name": folder.name,
        "folder_type": folder.folder_type,
        "sort_order": folder.sort_order,
        "created_at": folder.created_at,
        "updated_at": folder.updated_at,
        "children": [],
    }


def _conversation_export_payload(conversation: Conversation) -> dict:
    return {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "folder_id": conversation.folder_id,
        "title": conversation.title,
        "dify_conversation_id": conversation.dify_conversation_id,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
        "source": "dify",
        "messages": [],
        "note": "Conversation body is stored in Dify and will be hydrated by the Dify proxy step.",
    }


def _conversation_export_markdown(conversation: Conversation) -> str:
    dify_id = conversation.dify_conversation_id or "未绑定"
    folder_id = str(conversation.folder_id) if conversation.folder_id else "未归档"
    return "\n".join(
        [
            f"# {conversation.title}",
            "",
            f"- 知行会话 ID：`{conversation.id}`",
            f"- Dify 会话 ID：`{dify_id}`",
            f"- 工作区文件夹：`{folder_id}`",
            f"- 创建时间：{conversation.created_at.isoformat()}",
            f"- 更新时间：{conversation.updated_at.isoformat()}",
            "",
            "> 会话正文由 Dify 保存；Dify 代理步骤完成后将在此导出完整消息。",
            "",
        ]
    )


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


@router.get("/folders/tree", response_model=list[FolderTreeNode])
async def folder_tree(
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(WorkspaceFolder)
        .where(WorkspaceFolder.user_id == user_id)
        .order_by(WorkspaceFolder.sort_order, WorkspaceFolder.created_at)
    )
    folders = list(await db.scalars(stmt))
    nodes = {folder.id: _folder_node(folder) for folder in folders}
    roots: list[dict] = []

    for folder in folders:
        node = nodes[folder.id]
        if folder.parent_id and folder.parent_id in nodes:
            nodes[folder.parent_id]["children"].append(node)
        else:
            roots.append(node)

    return roots


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
    body: ConversationCreate, db: AsyncSession = Depends(get_db)
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


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
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


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await db.delete(conversation)
    await db.commit()


@router.get("/conversations/{conversation_id}/export")
async def export_conversation(
    conversation_id: uuid.UUID,
    format: ExportFormat = Query("markdown"),
    db: AsyncSession = Depends(get_db),
):
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if format == "json":
        return _conversation_export_payload(conversation)

    return Response(
        content=_conversation_export_markdown(conversation),
        media_type="text/markdown; charset=utf-8",
    )
