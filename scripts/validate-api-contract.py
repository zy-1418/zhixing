#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "api"))
sys.path.insert(0, str(ROOT / "services"))

from main import app  # noqa: E402
from routers.tasks import router as tasks_router  # noqa: E402


def _assert_openapi_path(paths: dict, path: str, method: str) -> None:
    assert path in paths, f"missing OpenAPI path: {path}"
    assert method in paths[path], f"missing {method.upper()} for {path}"


def validate_openapi_contract() -> None:
    paths = app.openapi()["paths"]
    expected = {
        "/health": "get",
        "/api/v1/auth/register": "post",
        "/api/v1/tasks": "get",
        "/api/v1/tasks/sop": "post",
        "/api/v1/tasks/{identifier}": "get",
        "/api/v1/tasks/{identifier}/retry": "post",
        "/api/v1/tasks/metagpt/{job_id}": "get",
        "/api/v1/tasks/metagpt/{job_id}/optimize": "post",
        "/api/v1/tasks/queue": "get",
        "/api/v1/tasks/calendar": "get",
        "/api/v1/dify/chat": "post",
        "/api/v1/social/posts": "get",
        "/api/v1/extensions/search": "get",
        "/api/v1/extensions/commerce/status": "get",
        "/api/v1/extensions/knowledge/graph": "get",
    }
    for path, method in expected.items():
        _assert_openapi_path(paths, path, method)

    websocket_paths = {
        getattr(route, "path", None)
        for route in tasks_router.routes
        if "websocket" in route.__class__.__name__.lower()
    }
    assert "/tasks/{job_id}/logs" in websocket_paths, "missing task log WebSocket"
    print(f"openapi ok: {len(paths)} paths; websocket ok")


def validate_workflow_state() -> None:
    state_path = ROOT / ".cursor" / "WORKFLOW_STATE.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["current_step"] == "p4-final"
    assert state["auto_continue"] is False
    incomplete = [
        step["id"]
        for step in state["steps"]
        if step.get("status") != "completed"
    ]
    assert not incomplete, f"incomplete workflow steps: {incomplete}"
    print(f"workflow ok: {len(state['steps'])} steps completed")


def main() -> None:
    validate_openapi_contract()
    validate_workflow_state()


if __name__ == "__main__":
    main()
