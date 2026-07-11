from __future__ import annotations

from main import app
from routers import tasks


REQUIRED_OPENAPI_PATHS = {
    "/health",
    "/api/v1/auth/register",
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


def main() -> None:
    paths = app.openapi()["paths"]
    missing = sorted(path for path in REQUIRED_OPENAPI_PATHS if path not in paths)
    if missing:
        raise SystemExit(f"missing OpenAPI paths: {missing}")

    task_ws_paths = {
        route.path
        for route in tasks.router.routes
        if route.__class__.__name__ == "APIWebSocketRoute"
    }
    if "/tasks/{job_id}/logs" not in task_ws_paths:
        raise SystemExit(f"missing task log websocket: {task_ws_paths}")

    print(f"openapi ok {len(paths)} paths; websocket ok")


if __name__ == "__main__":
    main()
