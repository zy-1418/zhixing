from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "api"))
sys.path.insert(0, str(ROOT / "services"))

from main import app  # noqa: E402


REQUIRED_HTTP_PATHS = {
    "/health",
    "/api/v1/auth/register",
    "/api/v1/tasks/sop",
    "/api/v1/tasks/{identifier}",
    "/api/v1/tasks/{identifier}/retry",
    "/api/v1/tasks/queue",
    "/api/v1/tasks/calendar",
    "/api/v1/dify/chat",
    "/api/v1/social/posts",
    "/api/v1/workspace/tree",
    "/api/v1/notes",
}


def main() -> None:
    paths = app.openapi()["paths"]
    missing = sorted(REQUIRED_HTTP_PATHS - set(paths))
    if missing:
        raise SystemExit(f"missing OpenAPI paths: {missing}")

    workflow = json.loads((ROOT / ".cursor" / "WORKFLOW_STATE.json").read_text())
    incomplete = [
        step["id"]
        for step in workflow["steps"]
        if step.get("status") != "completed"
    ]
    if workflow.get("auto_continue") is not False:
        raise SystemExit("auto_continue must be false after final delivery")
    if incomplete:
        raise SystemExit(f"incomplete workflow steps: {incomplete}")

    for required_doc in ("docs/PLAN.md", "docs/BLOCKERS.md", "docs/RELEASE.md"):
        if not (ROOT / required_doc).is_file():
            raise SystemExit(f"missing required doc: {required_doc}")

    print(f"openapi ok {len(paths)}")


if __name__ == "__main__":
    main()
