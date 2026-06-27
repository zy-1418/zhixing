from __future__ import annotations

import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# services/ on path for metagpt_bridge package
_SERVICES = Path(__file__).resolve().parents[2]
if str(_SERVICES) not in sys.path:
    sys.path.insert(0, str(_SERVICES))

from metagpt_bridge.client import MetaGPTBridgeError, MetaGPTClient
from metagpt_bridge.templates import build_idea, write_spec_file

from config import settings
from database import get_db
from models.task import Task
from priority_queue import priority_queue

router = APIRouter(prefix="/tasks", tags=["tasks"])

WorkflowType = Literal["research", "writing", "search", "custom"]
Priority = Literal["high", "medium", "low"]


class SubmitSopTaskRequest(BaseModel):
    user_id: Optional[uuid.UUID] = None
    folder_id: Optional[uuid.UUID] = None
    instruction: str = Field(..., min_length=1, description="一句话布置")
    workflow_type: WorkflowType = "custom"
    priority: Priority = "medium"
    name: Optional[str] = None
    context_notes: Optional[str] = Field(None, description="工作区笔记上下文")
    due_at: Optional[datetime] = None
    run_tests: bool = True
    skip_dev: bool = False


class TaskResponse(BaseModel):
    zhixing_task_id: uuid.UUID
    metagpt_job_id: str
    name: str
    status: str
    queue: Optional[dict] = None


class TaskRecordResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    folder_id: Optional[uuid.UUID]
    instruction: str
    name: Optional[str]
    workflow_type: str
    priority: str
    status: str
    metagpt_job_id: Optional[str]
    due_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


def _slugify(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s.strip()).lower()
    return (s[:48] or "task").strip("-")


@router.post("/sop", response_model=TaskResponse)
async def submit_sop_task(
    body: SubmitSopTaskRequest,
    db: AsyncSession = Depends(get_db),
):
    client = MetaGPTClient(base_url=settings.metagpt_x_api)
    name = body.name or _slugify(body.instruction)[:32]
    name = f"{name}-{uuid.uuid4().hex[:6]}"
    task: Task | None = None

    if body.user_id is not None:
        task = Task(
            user_id=body.user_id,
            folder_id=body.folder_id,
            instruction=body.instruction,
            name=name,
            workflow_type=body.workflow_type,
            priority=body.priority,
            status="queued",
            due_at=body.due_at,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        priority_queue.enqueue(str(task.id), body.priority)

    if body.context_notes:
        write_spec_file(name, body.context_notes, Path(settings.metagpt_root))

    idea = build_idea(
        body.instruction,
        body.workflow_type,
        context_snippet=body.context_notes or "",
    )

    try:
        job = await client.create_sop_project(
            name=name,
            idea=idea,
            run_tests=body.run_tests,
            skip_dev=body.skip_dev,
        )
    except MetaGPTBridgeError as e:
        if task is not None:
            task.status = "blocked"
            await db.commit()
        raise HTTPException(status_code=502, detail=str(e)) from e
    except Exception as e:
        if task is not None:
            task.status = "blocked"
            await db.commit()
        raise HTTPException(status_code=503, detail=f"MetaGPT-X unreachable: {e}") from e

    job_id = job.get("id") or job.get("job_id") or str(job)
    if task is None:
        task_id = uuid.uuid4()
    else:
        task.metagpt_job_id = str(job_id)
        task.status = job.get("status", "queued")
        await db.commit()
        task_id = task.id

    try:
        queue = await client.queue_status()
    except Exception:
        queue = priority_queue.snapshot()

    return TaskResponse(
        zhixing_task_id=task_id,
        metagpt_job_id=str(job_id),
        name=name,
        status=job.get("status", "queued"),
        queue=queue,
    )


@router.get("/queue")
async def get_queue():
    client = MetaGPTClient(base_url=settings.metagpt_x_api)
    try:
        return await client.queue_status()
    except Exception as e:
        return {"metagpt_error": str(e), "local_queue": priority_queue.snapshot()}


@router.get("", response_model=list[TaskRecordResponse])
async def list_tasks(
    user_id: uuid.UUID = Query(...),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Task).where(Task.user_id == user_id)
    if status:
        stmt = stmt.where(Task.status == status)
    stmt = stmt.order_by(Task.created_at.desc())
    result = await db.scalars(stmt)
    return result.all()


@router.get("/calendar", response_model=list[TaskRecordResponse])
async def task_calendar(
    user_id: uuid.UUID = Query(...),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Task).where(Task.user_id == user_id, Task.due_at.is_not(None))
    if start is not None:
        stmt = stmt.where(Task.due_at >= start)
    if end is not None:
        stmt = stmt.where(Task.due_at <= end)
    stmt = stmt.order_by(Task.due_at.asc())
    result = await db.scalars(stmt)
    return result.all()


@router.get("/{task_id}", response_model=TaskRecordResponse)
async def get_task(task_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/metagpt/{job_id}")
async def get_metagpt_job(job_id: str):
    client = MetaGPTClient(base_url=settings.metagpt_x_api)
    try:
        return await client.get_project(job_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/metagpt/{job_id}/optimize")
async def optimize_metagpt_job(job_id: str, qa_fix_rounds: int = 3):
    client = MetaGPTClient(base_url=settings.metagpt_x_api)
    try:
        return await client.optimize(job_id, qa_fix_rounds=qa_fix_rounds)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.websocket("/metagpt/{job_id}/logs")
async def stream_metagpt_logs(websocket: WebSocket, job_id: str):
    await websocket.accept()
    client = MetaGPTClient(base_url=settings.metagpt_x_api)
    try:
        async for message in client.stream_logs_ws(job_id):
            await websocket.send_text(message)
    except WebSocketDisconnect:
        return
    except Exception as exc:
        await websocket.send_json(
            {
                "type": "error",
                "detail": f"MetaGPT-X log stream unavailable: {exc}",
            }
        )
    finally:
        await websocket.close()
