from __future__ import annotations

from main import app
from routers.tasks import router as tasks_router


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
    "/api/v1/dify/chat",
    "/api/v1/social/posts",
    "/api/v1/extensions/search",
    "/api/v1/extensions/profiles/{user_id}",
    "/api/v1/extensions/commerce/status",
    "/api/v1/extensions/knowledge/graph",
    "/api/v1/workspace/tree",
    "/api/v1/notes",
}


def main() -> None:
    paths = app.openapi()["paths"]
    missing = sorted(REQUIRED_HTTP_PATHS - set(paths))
    if missing:
        raise AssertionError(f"missing OpenAPI paths: {missing}")

    websocket_paths = {route.path for route in tasks_router.routes}
    if "/tasks/{job_id}/logs" not in websocket_paths:
        raise AssertionError("missing task log WebSocket route")

    print(f"openapi ok {len(paths)} paths; websocket ok")


if __name__ == "__main__":
    main()
