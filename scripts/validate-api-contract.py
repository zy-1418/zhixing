#!/usr/bin/env python3
"""Validate the Zhixing API and workflow completion contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "api"))
sys.path.insert(0, str(ROOT / "services"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_workflow() -> None:
    state_path = ROOT / ".cursor" / "WORKFLOW_STATE.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    require(state["auto_continue"] is False, "auto_continue must be false")
    require(state["current_step"] == "p4-final", "current_step must be p4-final")
    incomplete = [
        step["id"] for step in state["steps"] if step.get("status") != "completed"
    ]
    require(not incomplete, f"incomplete workflow steps: {incomplete}")
    require((ROOT / "docs" / "RELEASE.md").exists(), "docs/RELEASE.md is missing")
    require((ROOT / "docs" / "BLOCKERS.md").exists(), "docs/BLOCKERS.md is missing")


def validate_openapi() -> None:
    from main import app
    from routers.tasks import router as tasks_router

    paths = app.openapi()["paths"]
    required_paths = {
        "/health",
        "/api/v1/auth/register",
        "/api/v1/tasks/sop",
        "/api/v1/tasks/{task_id}",
        "/api/v1/tasks/{task_id}/retry",
        "/api/v1/tasks/metagpt/{job_id}",
        "/api/v1/tasks/metagpt/{job_id}/optimize",
        "/api/v1/tasks/queue",
        "/api/v1/tasks/calendar",
        "/api/v1/dify/chat",
        "/api/v1/social/posts",
        "/api/v1/extensions/search",
        "/api/v1/extensions/commerce/status",
        "/api/v1/extensions/knowledge/graph",
    }
    missing = sorted(required_paths - set(paths))
    require(not missing, f"missing OpenAPI paths: {missing}")

    task_status_methods = paths["/api/v1/tasks/{task_id}"]
    require("get" in task_status_methods, "task status GET is missing")
    require("patch" in task_status_methods, "task update PATCH is missing")
    require("delete" in task_status_methods, "task delete DELETE is missing")
    require(
        "post" in paths["/api/v1/tasks/{task_id}/retry"],
        "task retry POST is missing",
    )
    require(
        any(
            getattr(route, "path", "") == "/tasks/{job_id}/logs"
            for route in tasks_router.routes
        ),
        "task logs WebSocket route is missing",
    )


def main() -> None:
    validate_workflow()
    validate_openapi()
    print("workflow ok")
    print("openapi ok")
    print("websocket ok")


if __name__ == "__main__":
    main()
