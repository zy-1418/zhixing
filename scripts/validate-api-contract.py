from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "api"))
sys.path.insert(0, str(ROOT / "services"))


def _assert_workflow_complete() -> None:
    state_path = ROOT / ".cursor" / "WORKFLOW_STATE.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    incomplete = [
        step["id"]
        for step in state.get("steps", [])
        if step.get("status") != "completed"
    ]
    assert not incomplete, f"incomplete workflow steps: {incomplete}"
    assert state.get("current_step") == "p4-final", state.get("current_step")
    assert state.get("auto_continue") is False, state.get("auto_continue")


def _assert_openapi_contract() -> None:
    from main import app

    paths = app.openapi()["paths"]
    expected = {
        "/health",
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/tasks",
        "/api/v1/tasks/sop",
        "/api/v1/tasks/{identifier}",
        "/api/v1/tasks/{identifier}/retry",
        "/api/v1/tasks/metagpt/{job_id}",
        "/api/v1/tasks/metagpt/{job_id}/optimize",
        "/api/v1/tasks/queue",
        "/api/v1/tasks/calendar",
        "/api/v1/workspace/tree",
        "/api/v1/notes",
        "/api/v1/dify/chat",
        "/api/v1/social/posts",
        "/api/v1/extensions/search",
        "/api/v1/extensions/profiles/{user_id}",
        "/api/v1/extensions/commerce/status",
        "/api/v1/extensions/knowledge/graph",
    }
    missing = sorted(expected - set(paths))
    assert not missing, f"missing OpenAPI paths: {missing}"


def _assert_task_log_websocket() -> None:
    from routers.tasks import router

    websocket_paths = {
        getattr(route, "path", None)
        for route in router.routes
        if route.__class__.__name__ == "APIWebSocketRoute"
    }
    assert "/tasks/{job_id}/logs" in websocket_paths, websocket_paths


def main() -> None:
    _assert_workflow_complete()
    _assert_openapi_contract()
    _assert_task_log_websocket()
    print("workflow ok")
    print("openapi ok")
    print("websocket ok")


if __name__ == "__main__":
    main()
