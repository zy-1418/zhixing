#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "api"))
sys.path.insert(0, str(ROOT / "services"))

from main import app  # noqa: E402
from routers.tasks import router as tasks_router  # noqa: E402


REQUIRED_OPENAPI_PATHS = {
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
    "/api/v1/workspace/tree",
    "/api/v1/notes",
    "/api/v1/extensions/search",
    "/api/v1/extensions/profiles/{user_id}",
    "/api/v1/extensions/commerce/status",
    "/api/v1/extensions/knowledge/graph",
}


def main() -> None:
    paths = app.openapi()["paths"]
    missing = sorted(REQUIRED_OPENAPI_PATHS - paths.keys())
    if missing:
        raise SystemExit(f"Missing OpenAPI paths: {missing}")

    websocket_paths = {
        getattr(route, "path", None)
        for route in tasks_router.routes
        if getattr(route, "path", None)
    }
    if "/tasks/{job_id}/logs" not in websocket_paths:
        raise SystemExit("Missing task log WebSocket route: /tasks/{job_id}/logs")

    print(f"openapi ok {len(paths)} paths; websocket ok")


if __name__ == "__main__":
    main()
