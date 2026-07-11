from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "services" / "api"
SERVICES = ROOT / "services"

for path in (str(API), str(SERVICES)):
    if path not in sys.path:
        sys.path.insert(0, path)

from main import app  # noqa: E402
from routers.tasks import router as tasks_router  # noqa: E402


REQUIRED_OPENAPI_PATHS = {
    "/health",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/workspace/tree",
    "/api/v1/notes",
    "/api/v1/dify/chat",
    "/api/v1/social/posts",
    "/api/v1/extensions/search",
    "/api/v1/tasks",
    "/api/v1/tasks/sop",
    "/api/v1/tasks/calendar",
    "/api/v1/tasks/queue",
    "/api/v1/tasks/{identifier}",
    "/api/v1/tasks/{identifier}/retry",
    "/api/v1/tasks/metagpt/{job_id}",
    "/api/v1/tasks/metagpt/{job_id}/optimize",
}


def main() -> None:
    paths = app.openapi()["paths"]
    missing = sorted(REQUIRED_OPENAPI_PATHS - set(paths))
    if missing:
        raise SystemExit(f"missing OpenAPI paths: {missing}")

    websocket_paths = {
        getattr(route, "path", None)
        for route in tasks_router.routes
        if getattr(route, "path", None)
    }
    if "/tasks/{job_id}/logs" not in websocket_paths:
        raise SystemExit("missing task log WebSocket route")

    print(f"openapi ok: {len(paths)} paths")
    print("websocket ok: /api/v1/tasks/{job_id}/logs")


if __name__ == "__main__":
    main()
