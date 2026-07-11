from __future__ import annotations

import json
from pathlib import Path

from main import app
from routers import tasks


ROOT = Path(__file__).resolve().parents[1]


def _assert_required_docs() -> None:
    for relative in [
        "docs/PLAN.md",
        "docs/STACK.md",
        "docs/ARCHITECTURE.md",
        "docs/METAGPT_INTEGRATION.md",
        ".cursor/WORKFLOW_STATE.json",
        "docs/RELEASE.md",
        "docs/BLOCKERS.md",
    ]:
        path = ROOT / relative
        assert path.exists(), f"missing required document: {relative}"


def _assert_openapi_contract() -> None:
    paths = app.openapi()["paths"]
    required = [
        "/health",
        "/api/v1/auth/register",
        "/api/v1/tasks/sop",
        "/api/v1/tasks/{identifier}",
        "/api/v1/tasks/{identifier}/retry",
        "/api/v1/tasks/metagpt/{job_id}",
        "/api/v1/tasks/metagpt/{job_id}/optimize",
        "/api/v1/tasks/queue",
        "/api/v1/tasks/calendar",
        "/api/v1/dify/chat",
        "/api/v1/social/posts",
        "/api/v1/extensions/search",
        "/api/v1/extensions/profiles/{user_id}",
        "/api/v1/extensions/commerce/status",
        "/api/v1/extensions/knowledge/graph",
    ]
    for path in required:
        assert path in paths, path
    print(f"openapi ok {len(paths)} paths")


def _assert_websocket_contract() -> None:
    websocket_paths = {
        getattr(route, "path", "")
        for route in tasks.router.routes
        if route.__class__.__name__ == "APIWebSocketRoute"
    }
    assert "/tasks/{job_id}/logs" in websocket_paths
    print("websocket ok")


def _assert_workflow_complete() -> None:
    state = json.loads((ROOT / ".cursor/WORKFLOW_STATE.json").read_text())
    assert state["auto_continue"] is False
    assert state["current_step"] == "p4-final"
    assert all(step["status"] == "completed" for step in state["steps"])
    print(f"workflow ok {len(state['steps'])} steps")


if __name__ == "__main__":
    _assert_required_docs()
    _assert_openapi_contract()
    _assert_websocket_contract()
    _assert_workflow_complete()
