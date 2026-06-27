from __future__ import annotations

import re
import sys
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.task import Task
# services/ on path for metagpt_bridge package
_SERVICES = Path(__file__).resolve().parents[2]
if str(_SERVICES) not in sys.path:
    sys.path.insert(0, str(_SERVICES))

from metagpt_bridge.client import MetaGPTBridgeError, MetaGPTClient
from metagpt_bridge.templates import build_idea, write_spec_file

from config import settings

router = APIRouter(prefix="/tasks", tags=["tasks"])

WorkflowType = Literal["research", "writing", "search", "custom"]
Priority = Literal["high", "medium", "low"]


class SubmitSopTaskRequest(BaseModel):
    user_id: Optional[uuid.UUID] = Field(None, description="登录后可由客户端传入")
    folder_id: Optional[uuid.UUID] = None
    instruction: str = Field(..., min_length=1, description="一句话布置")
    workflow_type: WorkflowType = "custom"
    priority: Priority = "medium"
    name: Optional[str] = None
    context_notes: Optional[str] = Field(None, description="工作区笔记上下文")
    run_tests: bool = True
    skip_dev: bool = False


class TaskResponse(BaseModel):
    zhixing_task_id: str
    metagpt_job_id: Optional[str]
    name: str
    status: str
    queue: Optional[dict] = None
    detail: Optional[str] = None


class StoredTaskResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    folder_id: Optional[uuid.UUID]
    instruction: str
    name: Optional[str]
    workflow_type: str
    priority: str
    status: str
    metagpt_job_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


def _slugify(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s.strip()).lower()
    return (s[:48] or "task").strip("-")


async def _try_queue_status(client: MetaGPTClient) -> dict[str, Any] | None:
    try:
        return await client.queue_status()
    except Exception:
        return None


@router.post("/sop", response_model=TaskResponse)
async def submit_sop_task(
    body: SubmitSopTaskRequest,
    db: AsyncSession = Depends(get_db),
):
    client = MetaGPTClient(base_url=settings.metagpt_x_api)
    name = body.name or _slugify(body.instruction)[:32]
    name = f"{name}-{uuid.uuid4().hex[:6]}"

    if body.context_notes:
        write_spec_file(name, body.context_notes, Path(settings.metagpt_root))

    idea = build_idea(
        body.instruction,
        body.workflow_type,
        context_snippet=body.context_notes or "",
    )

    task: Task | None = None
    if body.user_id is not None:
        task = Task(
            user_id=body.user_id,
            folder_id=body.folder_id,
            instruction=body.instruction,
            name=name,
            workflow_type=body.workflow_type,
            priority=body.priority,
            status="submitting",
        )
        db.add(task)
        await db.flush()

    try:
        job = await client.create_sop_project(
            name=name,
            idea=idea,
            run_tests=body.run_tests,
            skip_dev=body.skip_dev,
        )
        job_id = str(job.get("id") or job.get("job_id") or job)
        status = job.get("status", "queued")
        detail = None
    except (MetaGPTBridgeError, Exception) as e:
        if not settings.metagpt_stub_on_unreachable:
            raise HTTPException(status_code=503, detail=f"MetaGPT-X unreachable: {e}") from e
        job = {}
        job_id = f"metagpt-unreachable-{uuid.uuid4().hex[:8]}"
        status = "blocked"
        detail = f"MetaGPT-X unreachable in Cloud environment: {e}"

    queue = await _try_queue_status(client)

    if task is not None:
        task.metagpt_job_id = job_id
        task.status = status
        await db.commit()
        await db.refresh(task)
        zhixing_task_id = str(task.id)
    else:
        await db.rollback()
        zhixing_task_id = str(uuid.uuid4())

    return TaskResponse(
        zhixing_task_id=zhixing_task_id,
        metagpt_job_id=job_id,
        name=name,
        status=status,
        queue=queue,
        detail=detail,
    )


@router.get("/queue")
async def get_queue():
    client = MetaGPTClient(base_url=settings.metagpt_x_api)
    try:
        return await client.queue_status()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@router.get("", response_model=list[StoredTaskResponse])
async def list_tasks(
    user_id: uuid.UUID = Query(...),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Task).where(Task.user_id == user_id)
    if status is not None:
        stmt = stmt.where(Task.status == status)
    stmt = stmt.order_by(Task.created_at.desc())
    result = await db.scalars(stmt)
    return result.all()


@router.get("/calendar")
async def task_calendar(
    user_id: uuid.UUID = Query(...),
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Task).where(Task.user_id == user_id)
    if start is not None:
        stmt = stmt.where(Task.created_at >= datetime.combine(start, datetime.min.time()))
    if end is not None:
        stmt = stmt.where(Task.created_at <= datetime.combine(end, datetime.max.time()))
    stmt = stmt.order_by(Task.created_at)
    tasks = (await db.scalars(stmt)).all()
    days: dict[str, list[StoredTaskResponse]] = {}
    for task in tasks:
        key = task.created_at.date().isoformat()
        days.setdefault(key, []).append(StoredTaskResponse.model_validate(task))
    return {"items": days}


@router.get("/{task_id}", response_model=StoredTaskResponse)
async def get_task(task_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.websocket("/{task_id}/logs")
async def stream_task_logs(task_id: str, websocket: WebSocket):
    await websocket.accept()
    client = MetaGPTClient(base_url=settings.metagpt_x_api)
    try:
        async for message in client.stream_logs_ws(task_id):
            await websocket.send_text(message)
    except Exception as exc:
        await websocket.send_json(
            {
                "type": "blocked",
                "task_id": task_id,
                "message": f"MetaGPT-X logs unavailable: {exc}",
            }
        )
    finally:
        await websocket.close()


@router.post("/{task_id}/retry")
async def retry_task(task_id: uuid.UUID, qa_fix_rounds: int = 3, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if not task.metagpt_job_id:
        raise HTTPException(status_code=409, detail="Task has no MetaGPT job id")
    return await optimize_metagpt_job(task.metagpt_job_id, qa_fix_rounds=qa_fix_rounds)


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
