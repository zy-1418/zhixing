from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
for path in (ROOT / "services" / "api", ROOT / "services"):
    sys.path.insert(0, str(path))

from main import app  # noqa: E402
from routers.tasks import router as tasks_router  # noqa: E402


REQUIRED_HTTP_PATHS = {
    "/health",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/tasks",
    "/api/v1/tasks/sop",
    "/api/v1/tasks/calendar",
    "/api/v1/tasks/queue",
    "/api/v1/tasks/{identifier}",
    "/api/v1/tasks/{identifier}/retry",
    "/api/v1/dify/chat",
    "/api/v1/social/posts",
    "/api/v1/extensions/search",
    "/api/v1/extensions/profiles/{user_id}",
    "/api/v1/extensions/commerce/status",
}

REQUIRED_WEBSOCKET_PATHS = {
    "/api/v1/tasks/{job_id}/logs",
}


def main() -> None:
    openapi_paths = set(app.openapi()["paths"])
    missing_http = sorted(REQUIRED_HTTP_PATHS - openapi_paths)
    websocket_paths = {
        f"/api/v1{getattr(route, 'path', '')}" for route in tasks_router.routes
    }
    missing_ws = sorted(REQUIRED_WEBSOCKET_PATHS - websocket_paths)

    if missing_http or missing_ws:
        details = []
        if missing_http:
            details.append(f"missing HTTP paths: {missing_http}")
        if missing_ws:
            details.append(f"missing WebSocket paths: {missing_ws}")
        raise AssertionError("; ".join(details))

    print(
        "api contract ok: "
        f"{len(REQUIRED_HTTP_PATHS)} HTTP paths, "
        f"{len(REQUIRED_WEBSOCKET_PATHS)} WebSocket paths"
    )


if __name__ == "__main__":
    main()
