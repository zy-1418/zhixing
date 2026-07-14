from __future__ import annotations

import re
import sys
import uuid
from datetime import datetime, timezone
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
TaskStatus = Literal["pending", "queued", "running", "blocked", "completed", "failed"]

_priority_queue: list[dict[str, Any]] = []


class SubmitSopTaskRequest(BaseModel):
    instruction: str = Field(..., min_length=1, description="一句话布置")
    workflow_type: WorkflowType = "custom"
    priority: Priority = "medium"
    name: Optional[str] = None
    user_id: Optional[uuid.UUID] = None
    folder_id: Optional[uuid.UUID] = None
    due_at: Optional[datetime] = None
    context_notes: Optional[str] = Field(None, description="工作区笔记上下文")
    run_tests: bool = True
    skip_dev: bool = False


class TaskResponse(BaseModel):
    zhixing_task_id: str
    metagpt_job_id: str
    name: str
    status: str
    queue: Optional[dict] = None
    blocked_reason: Optional[str] = None


class LocalTaskCreate(BaseModel):
    user_id: uuid.UUID
    instruction: str = Field(..., min_length=1)
    name: str | None = None
    folder_id: uuid.UUID | None = None
    workflow_type: WorkflowType = "custom"
    priority: Priority = "medium"
    status: TaskStatus = "pending"
    due_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskUpdate(BaseModel):
    instruction: str | None = None
    name: str | None = None
    folder_id: uuid.UUID | None = None
    workflow_type: WorkflowType | None = None
    priority: Priority | None = None
    status: TaskStatus | None = None
    due_at: datetime | None = None
    completed_at: datetime | None = None
    metadata: dict[str, Any] | None = None


class TaskRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    folder_id: uuid.UUID | None
    instruction: str
    name: str | None
    workflow_type: str
    priority: str
    status: str
    metagpt_job_id: str | None
    due_at: datetime | None
    completed_at: datetime | None
    metadata: dict[str, Any] = Field(
        validation_alias="metadata_", serialization_alias="metadata"
    )
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class TaskStatusResponse(BaseModel):
    identifier: str
    zhixing_task_id: str | None = None
    metagpt_job_id: str | None = None
    name: str | None = None
    status: str
    local_status: str | None = None
    remote: dict[str, Any] | None = None
    blocked: bool = False
    reason: str | None = None


class TaskRetryResponse(BaseModel):
    identifier: str
    zhixing_task_id: str | None = None
    metagpt_job_id: str | None = None
    status: str
    optimize_result: dict[str, Any] | None = None
    blocked: bool = False
    reason: str | None = None
    qa_fix_rounds: int


def _slugify(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s.strip()).lower()
    return (s[:48] or "task").strip("-")


async def _rollback_quietly(db: AsyncSession) -> None:
    try:
        await db.rollback()
    except Exception:
        pass


async def _find_local_task(
    identifier: str, db: AsyncSession
) -> tuple[Task | None, str | None]:
    try:
        try:
            task_uuid = uuid.UUID(identifier)
        except ValueError:
            task_uuid = None

        if task_uuid is not None:
            task = await db.get(Task, task_uuid)
            if task is not None:
                return task, None

        task = await db.scalar(select(Task).where(Task.metagpt_job_id == identifier))
        return task, None
    except Exception as e:
        await _rollback_quietly(db)
        return None, f"PostgreSQL task lookup unavailable: {e}"


def _task_identity(identifier: str, task: Task | None) -> dict[str, str | None]:
    if task is None:
        return {
            "identifier": identifier,
            "zhixing_task_id": None,
            "metagpt_job_id": identifier,
            "name": None,
        }
    return {
        "identifier": identifier,
        "zhixing_task_id": str(task.id),
        "metagpt_job_id": task.metagpt_job_id,
        "name": task.name,
    }


@router.post("/sop", response_model=TaskResponse)
async def submit_sop_task(
    body: SubmitSopTaskRequest, db: AsyncSession = Depends(get_db)
):
    client = MetaGPTClient(base_url=settings.metagpt_x_api)
    name = body.name or _slugify(body.instruction)[:32]
    name = f"{name}-{uuid.uuid4().hex[:6]}"
    local_task: Task | None = None

    if body.user_id is not None:
        local_task = Task(
            user_id=body.user_id,
            folder_id=body.folder_id,
            instruction=body.instruction,
            name=name,
            workflow_type=body.workflow_type,
            priority=body.priority,
            status="queued",
            due_at=body.due_at,
            metadata_={"source": "metagpt-sop"},
        )
        db.add(local_task)
        await db.commit()
        await db.refresh(local_task)
        _enqueue_priority(local_task, body.priority)

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
        job = {"id": f"metagpt-unavailable-{uuid.uuid4().hex[:8]}", "status": "blocked"}
        blocked_reason = str(e)
    except Exception as e:
        job = {"id": f"metagpt-unavailable-{uuid.uuid4().hex[:8]}", "status": "blocked"}
        blocked_reason = f"MetaGPT-X unreachable: {e}"
    else:
        blocked_reason = None

    job_id = job.get("id") or job.get("job_id") or str(job)
    if local_task is not None:
        local_task.metagpt_job_id = str(job_id)
        local_task.status = job.get("status", "queued")
        if blocked_reason:
            local_task.metadata_ = {
                **(local_task.metadata_ or {}),
                "blocked_reason": blocked_reason,
            }
        await db.commit()

    queue = await _queue_status(client)

    return TaskResponse(
        zhixing_task_id=str(local_task.id if local_task else uuid.uuid4()),
        metagpt_job_id=str(job_id),
        name=name,
        status=job.get("status", "queued"),
        queue=queue,
        blocked_reason=blocked_reason,
    )


def _enqueue_priority(task: Task, priority: Priority) -> None:
    item = {
        "task_id": str(task.id),
        "priority": priority,
        "name": task.name,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "backend": "redis-placeholder",
        "redis_url": settings.redis_url,
    }
    if priority == "high":
        _priority_queue.insert(0, item)
    elif priority == "low":
        _priority_queue.append({**item, "defer_until_worker_idle": True})
    else:
        _priority_queue.append(item)


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    user_id: uuid.UUID = Query(...),
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Task).where(Task.user_id == user_id)
    if status:
        stmt = stmt.where(Task.status == status)
    stmt = stmt.order_by(Task.due_at.nulls_last(), Task.created_at.desc())
    result = await db.scalars(stmt)
    return result.all()


@router.post("", response_model=TaskRead, status_code=201)
async def create_task(body: LocalTaskCreate, db: AsyncSession = Depends(get_db)):
    task = Task(
        user_id=body.user_id,
        folder_id=body.folder_id,
        instruction=body.instruction,
        name=body.name,
        workflow_type=body.workflow_type,
        priority=body.priority,
        status=body.status,
        due_at=body.due_at,
        metadata_=body.metadata,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("/calendar", response_model=list[TaskRead])
async def task_calendar(
    user_id: uuid.UUID = Query(...),
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Task).where(Task.user_id == user_id)
    if start is not None:
        stmt = stmt.where(Task.due_at >= start)
    if end is not None:
        stmt = stmt.where(Task.due_at <= end)
    stmt = stmt.order_by(Task.due_at.nulls_last(), Task.created_at)
    result = await db.scalars(stmt)
    return result.all()


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: uuid.UUID, body: TaskUpdate, db: AsyncSession = Depends(get_db)
):
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    values = body.model_dump(exclude_unset=True)
    if "metadata" in values:
        values["metadata_"] = values.pop("metadata")
    for field, value in values.items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()


@router.get("/queue")
async def get_queue():
    client = MetaGPTClient(base_url=settings.metagpt_x_api)
    return await _queue_status(client)


async def _queue_status(client: MetaGPTClient) -> dict[str, Any]:
    try:
        remote = await client.queue_status()
        return {"remote": remote, "local_priority": _priority_queue}
    except Exception as e:
        return {
            "remote": None,
            "local_priority": _priority_queue,
            "blocked": True,
            "reason": f"MetaGPT-X queue unavailable: {e}",
        }


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
        return {
            "blocked": True,
            "job_id": job_id,
            "reason": f"MetaGPT-X optimize unavailable: {e}",
            "qa_fix_rounds": qa_fix_rounds,
        }


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str, db: AsyncSession = Depends(get_db)):
    local_task, db_error = await _find_local_task(task_id, db)
    identity = _task_identity(task_id, local_task)
    metagpt_job_id = identity["metagpt_job_id"]

    if local_task is not None and metagpt_job_id is None:
        return TaskStatusResponse(
            **identity,
            status=local_task.status,
            local_status=local_task.status,
            reason=db_error,
        )

    client = MetaGPTClient(base_url=settings.metagpt_x_api)
    remote_job_id = metagpt_job_id or task_id
    response_identity = {**identity, "metagpt_job_id": remote_job_id}
    try:
        remote = await client.get_project(remote_job_id)
    except Exception as e:
        reason_parts = [f"MetaGPT-X status unavailable: {e}"]
        if db_error:
            reason_parts.append(db_error)
        return TaskStatusResponse(
            **response_identity,
            status=local_task.status if local_task is not None else "blocked",
            local_status=local_task.status if local_task is not None else None,
            blocked=True,
            reason="; ".join(reason_parts),
        )

    remote_status = str(remote.get("status") or remote.get("state") or "unknown")
    return TaskStatusResponse(
        **response_identity,
        status=remote_status,
        local_status=local_task.status if local_task is not None else None,
        remote=remote,
        reason=db_error,
    )


@router.post("/{task_id}/retry", response_model=TaskRetryResponse)
async def retry_task(
    task_id: str, qa_fix_rounds: int = 3, db: AsyncSession = Depends(get_db)
):
    local_task, db_error = await _find_local_task(task_id, db)
    identity = _task_identity(task_id, local_task)
    metagpt_job_id = identity["metagpt_job_id"] if local_task is not None else task_id

    if local_task is not None and not metagpt_job_id:
        return TaskRetryResponse(
            **identity,
            status="blocked",
            blocked=True,
            reason="Task has no MetaGPT job id to retry",
            qa_fix_rounds=qa_fix_rounds,
        )

    client = MetaGPTClient(base_url=settings.metagpt_x_api)
    response_identity = {**identity, "metagpt_job_id": metagpt_job_id}
    try:
        result = await client.optimize(metagpt_job_id, qa_fix_rounds=qa_fix_rounds)
    except Exception as e:
        reason_parts = [f"MetaGPT-X optimize unavailable: {e}"]
        if db_error:
            reason_parts.append(db_error)
        return TaskRetryResponse(
            **response_identity,
            status="blocked",
            blocked=True,
            reason="; ".join(reason_parts),
            qa_fix_rounds=qa_fix_rounds,
        )

    if local_task is not None:
        local_task.status = "queued"
        local_task.metadata_ = {
            **(local_task.metadata_ or {}),
            "last_retry_at": datetime.now(timezone.utc).isoformat(),
            "last_retry_rounds": qa_fix_rounds,
        }
        try:
            await db.commit()
        except Exception:
            await _rollback_quietly(db)

    return TaskRetryResponse(
        **response_identity,
        status=str(result.get("status") or "retry_requested"),
        optimize_result=result,
        reason=db_error,
        qa_fix_rounds=qa_fix_rounds,
    )


@router.websocket("/{job_id}/logs")
async def stream_task_logs(websocket: WebSocket, job_id: str):
    await websocket.accept()
    client = MetaGPTClient(base_url=settings.metagpt_x_api)
    try:
        async for line in client.stream_logs_ws(job_id):
            await websocket.send_text(line)
    except Exception as e:
        await websocket.send_json(
            {
                "blocked": True,
                "job_id": job_id,
                "reason": f"MetaGPT-X WebSocket unavailable: {e}",
            }
        )
    finally:
        await websocket.close()
