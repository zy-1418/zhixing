from __future__ import annotations

import re
import sys
import uuid
from pathlib import Path
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

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
    instruction: str = Field(..., min_length=1, description="一句话布置")
    workflow_type: WorkflowType = "custom"
    priority: Priority = "medium"
    name: Optional[str] = None
    context_notes: Optional[str] = Field(None, description="工作区笔记上下文")
    run_tests: bool = True
    skip_dev: bool = False


class TaskResponse(BaseModel):
    zhixing_task_id: str
    metagpt_job_id: str
    name: str
    status: str
    queue: Optional[dict] = None


def _slugify(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s.strip()).lower()
    return (s[:48] or "task").strip("-")


@router.post("/sop", response_model=TaskResponse)
async def submit_sop_task(body: SubmitSopTaskRequest):
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

    try:
        job = await client.create_sop_project(
            name=name,
            idea=idea,
            run_tests=body.run_tests,
            skip_dev=body.skip_dev,
        )
    except MetaGPTBridgeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MetaGPT-X unreachable: {e}") from e

    job_id = job.get("id") or job.get("job_id") or str(job)
    queue = await client.queue_status()

    return TaskResponse(
        zhixing_task_id=str(uuid.uuid4()),
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
        raise HTTPException(status_code=503, detail=str(e)) from e


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
