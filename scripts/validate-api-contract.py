#!/usr/bin/env python3
"""Validate the public API contract used by Zhixing automation."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "api"))
sys.path.insert(0, str(ROOT / "services"))

from main import app  # noqa: E402
from routers import tasks  # noqa: E402


REQUIRED_HTTP_PATHS = [
    "/health",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/workspace/tree",
    "/api/v1/notes",
    "/api/v1/dify/chat",
    "/api/v1/tasks/sop",
    "/api/v1/tasks/{identifier}",
    "/api/v1/tasks/{identifier}/retry",
    "/api/v1/tasks/queue",
    "/api/v1/tasks/calendar",
    "/api/v1/social/posts",
    "/api/v1/extensions/search",
    "/api/v1/extensions/profiles/{user_id}",
    "/api/v1/extensions/commerce/status",
    "/api/v1/extensions/knowledge/graph",
]


def main() -> int:
    paths = app.openapi()["paths"]
    missing = [path for path in REQUIRED_HTTP_PATHS if path not in paths]
    if missing:
        raise SystemExit(f"Missing OpenAPI paths: {missing}")

    ws_paths = [getattr(route, "path", None) for route in tasks.router.routes]
    if "/{job_id}/logs" not in ws_paths:
        raise SystemExit("Missing task log WebSocket route: /{job_id}/logs")

    print(f"openapi ok {len(paths)} paths; websocket ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
