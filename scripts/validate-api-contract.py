from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "services" / "api"
SERVICES = ROOT / "services"

for path in (API, SERVICES):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


REQUIRED_HTTP_PATHS = {
    "/health",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
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

REQUIRED_DOCS = {
    "docs/PLAN.md",
    "docs/STACK.md",
    "docs/ARCHITECTURE.md",
    "docs/METAGPT_INTEGRATION.md",
    "docs/BLOCKERS.md",
    "docs/RELEASE.md",
}


def validate_openapi() -> None:
    from main import app

    paths = set(app.openapi()["paths"])
    missing = sorted(REQUIRED_HTTP_PATHS - paths)
    if missing:
        raise AssertionError(f"missing OpenAPI paths: {missing}")
    print(f"openapi ok {len(paths)}")


def validate_workflow_state() -> None:
    state_path = ROOT / ".cursor" / "WORKFLOW_STATE.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    steps = state.get("steps", [])
    incomplete = [step["id"] for step in steps if step.get("status") != "completed"]
    if incomplete:
        raise AssertionError(f"incomplete workflow steps: {incomplete}")
    if state.get("auto_continue") is not False:
        raise AssertionError("auto_continue must be false after release completion")
    if state.get("current_step") != "p4-final":
        raise AssertionError("current_step must remain p4-final after completion")
    print(f"workflow ok {len(steps)}")


def validate_docs() -> None:
    missing = sorted(path for path in REQUIRED_DOCS if not (ROOT / path).exists())
    if missing:
        raise AssertionError(f"missing docs: {missing}")
    print(f"docs ok {len(REQUIRED_DOCS)}")


def main() -> None:
    validate_openapi()
    validate_workflow_state()
    validate_docs()


if __name__ == "__main__":
    main()
