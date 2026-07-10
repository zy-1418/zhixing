#!/usr/bin/env python3
"""Validate the Zhixing API contract used by the automation workflow."""
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "services" / "api"), str(ROOT / "services")]

from main import app  # noqa: E402
from routers.tasks import router as tasks_router  # noqa: E402


REQUIRED_HTTP_PATHS = {
    "/health",
    "/api/v1/auth/register",
    "/api/v1/tasks",
    "/api/v1/tasks/sop",
    "/api/v1/tasks/calendar",
    "/api/v1/tasks/queue",
    "/api/v1/tasks/{identifier}",
    "/api/v1/tasks/{identifier}/retry",
    "/api/v1/tasks/metagpt/{job_id}",
    "/api/v1/tasks/metagpt/{job_id}/optimize",
    "/api/v1/workspace/tree",
    "/api/v1/notes",
    "/api/v1/dify/chat",
    "/api/v1/social/posts",
    "/api/v1/extensions/search",
    "/api/v1/extensions/profiles/{user_id}",
    "/api/v1/extensions/commerce/status",
    "/api/v1/extensions/knowledge/graph",
}


def validate_openapi() -> None:
    paths = app.openapi()["paths"]
    missing = sorted(REQUIRED_HTTP_PATHS - set(paths))
    if missing:
        raise SystemExit(f"Missing OpenAPI paths: {', '.join(missing)}")
    print(f"openapi ok {len(paths)}")


def validate_websocket() -> None:
    websocket_paths = {
        getattr(route, "path", "") for route in tasks_router.routes if "WebSocket" in type(route).__name__
    }
    if "/tasks/{job_id}/logs" not in websocket_paths:
        raise SystemExit("Missing task log WebSocket route: /tasks/{job_id}/logs")
    print("websocket ok")


def validate_workflow_state() -> None:
    state_path = ROOT / ".cursor" / "WORKFLOW_STATE.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    incomplete = [step["id"] for step in state["steps"] if step["status"] != "completed"]
    if incomplete:
        raise SystemExit(f"Incomplete workflow steps: {', '.join(incomplete)}")
    if state["current_step"] != "p4-final":
        raise SystemExit(f"Unexpected current_step: {state['current_step']}")
    if state["auto_continue"] is not False:
        raise SystemExit("auto_continue must be false after release completion")
    print(f"workflow ok {len(state['steps'])} steps")


def main() -> None:
    validate_openapi()
    validate_websocket()
    validate_workflow_state()


if __name__ == "__main__":
    main()
