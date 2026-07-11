from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "api"))
sys.path.insert(0, str(ROOT / "services"))

from main import app  # noqa: E402
from routers.tasks import router as tasks_router  # noqa: E402


REQUIRED_HTTP_PATHS = {
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


def validate_openapi() -> None:
    paths = app.openapi()["paths"]
    missing = sorted(REQUIRED_HTTP_PATHS.difference(paths))
    if missing:
        raise AssertionError(f"missing OpenAPI paths: {missing}")
    print(f"openapi ok: {len(paths)} paths")


def validate_websocket() -> None:
    paths = {getattr(route, "path", "") for route in tasks_router.routes}
    if "/tasks/{job_id}/logs" not in paths:
        raise AssertionError("missing task log WebSocket: /tasks/{job_id}/logs")
    print("websocket ok")


def validate_workflow_state() -> None:
    state_path = ROOT / ".cursor" / "WORKFLOW_STATE.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    incomplete = [
        step["id"]
        for step in state["steps"]
        if step.get("status") != "completed"
    ]
    if state.get("auto_continue") is not False:
        raise AssertionError("auto_continue must be false after final release")
    if incomplete:
        raise AssertionError(f"incomplete workflow steps: {incomplete}")
    print(
        "workflow ok:"
        f" current_step={state.get('current_step')}, steps={len(state['steps'])}"
    )


def main() -> None:
    validate_openapi()
    validate_websocket()
    validate_workflow_state()


if __name__ == "__main__":
    main()
