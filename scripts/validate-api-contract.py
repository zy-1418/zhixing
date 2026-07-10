from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "services" / "api"
SERVICES_DIR = ROOT / "services"

for path in (API_DIR, SERVICES_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from main import app  # noqa: E402
from routers import tasks as task_routes  # noqa: E402


REQUIRED_HTTP_PATHS = {
    "/health",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/tasks/sop",
    "/api/v1/tasks/{identifier}",
    "/api/v1/tasks/{identifier}/retry",
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
    paths = set(app.openapi()["paths"])
    missing = sorted(REQUIRED_HTTP_PATHS - paths)
    if missing:
        raise AssertionError(f"Missing HTTP contract paths: {missing}")

    websocket_paths = {
        getattr(route, "path", "")
        for route in task_routes.router.routes
        if route.__class__.__name__ == "APIWebSocketRoute"
    }
    if "/tasks/{job_id}/logs" not in websocket_paths:
        raise AssertionError("Missing WebSocket contract path: /tasks/{job_id}/logs")

    print("API contract ok")


if __name__ == "__main__":
    main()
