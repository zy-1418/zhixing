from __future__ import annotations

import json
from pathlib import Path

from main import app
from routers.tasks import router as tasks_router


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    "docs/PLAN.md",
    "docs/STACK.md",
    "docs/ARCHITECTURE.md",
    "docs/METAGPT_INTEGRATION.md",
    "docs/BLOCKERS.md",
    "docs/RELEASE.md",
    ".cursor/WORKFLOW_STATE.json",
]

REQUIRED_HTTP_PATHS = {
    "/health",
    "/api/v1/auth/register",
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


def assert_required_docs() -> None:
    missing = [path for path in REQUIRED_DOCS if not (ROOT / path).exists()]
    if missing:
        raise AssertionError(f"missing required docs: {missing}")


def assert_workflow_completed() -> None:
    state_path = ROOT / ".cursor/WORKFLOW_STATE.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    steps = state.get("steps", [])
    incomplete = [step["id"] for step in steps if step.get("status") != "completed"]

    if state.get("auto_continue") is not False:
        raise AssertionError("auto_continue must be false after final delivery")
    if state.get("current_step") != "p4-final":
        raise AssertionError("current_step must remain p4-final after final delivery")
    if incomplete:
        raise AssertionError(f"incomplete workflow steps: {incomplete}")


def assert_openapi_contract() -> None:
    paths = app.openapi()["paths"]
    missing = sorted(REQUIRED_HTTP_PATHS - set(paths))
    if missing:
        raise AssertionError(f"missing OpenAPI paths: {missing}")
    print(f"openapi ok {len(paths)} paths")


def assert_task_websocket_contract() -> None:
    websocket_paths = {
        getattr(route, "path", None)
        for route in tasks_router.routes
        if route.__class__.__name__ == "APIWebSocketRoute"
    }
    if "/tasks/{job_id}/logs" not in websocket_paths:
        raise AssertionError("missing task log WebSocket route")
    print("websocket ok")


def main() -> None:
    assert_required_docs()
    assert_workflow_completed()
    assert_openapi_contract()
    assert_task_websocket_contract()
    print("workflow ok")


if __name__ == "__main__":
    main()
