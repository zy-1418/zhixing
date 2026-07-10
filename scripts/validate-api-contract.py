#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import socket
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "api"))
sys.path.insert(0, str(ROOT / "services"))

from fastapi.testclient import TestClient  # noqa: E402
from main import app  # noqa: E402


def assert_workflow_complete() -> None:
    state = json.loads((ROOT / ".cursor" / "WORKFLOW_STATE.json").read_text())
    assert state["auto_continue"] is False
    assert state["current_step"] == "p4-final"
    assert all(step["status"] == "completed" for step in state["steps"])


def assert_docs_complete() -> None:
    plan = (ROOT / "docs" / "PLAN.md").read_text()
    release = (ROOT / "docs" / "RELEASE.md").read_text()
    blockers = (ROOT / "docs" / "BLOCKERS.md").read_text()
    for marker in ("**P0**", "**P1**", "**P2**", "**P3**", "**P4**"):
        assert marker in plan and "completed" in plan
    assert "auto_continue=false" in release
    assert "127.0.0.1:8000" in blockers


def assert_openapi_contract() -> None:
    paths = app.openapi()["paths"]
    required = {
        "/health",
        "/api/v1/auth/register",
        "/api/v1/tasks/sop",
        "/api/v1/tasks/{identifier}",
        "/api/v1/tasks/{identifier}/retry",
        "/api/v1/tasks/queue",
        "/api/v1/tasks/calendar",
        "/api/v1/dify/chat",
        "/api/v1/social/posts",
    }
    missing = sorted(required - set(paths))
    assert not missing, f"missing OpenAPI paths: {missing}"


def assert_task_blocked_contract() -> None:
    client = TestClient(app)
    status = client.get("/api/v1/tasks/metagpt-unavailable-smoke")
    assert status.status_code == 200, status.text
    status_data = status.json()
    assert status_data["status"] == "blocked"
    assert status_data["blocked"] is True
    assert status_data["metagpt_job_id"] == "metagpt-unavailable-smoke"

    retry = client.post(
        "/api/v1/tasks/metagpt-unavailable-smoke/retry",
        params={"qa_fix_rounds": 2},
    )
    assert retry.status_code == 200, retry.text
    retry_data = retry.json()
    assert retry_data["blocked"] is True
    assert retry_data["metagpt_job_id"] == "metagpt-unavailable-smoke"
    assert retry_data["qa_fix_rounds"] == 2


def assert_cloud_blockers() -> None:
    assert shutil.which("docker") is None
    assert shutil.which("flutter") is None
    sock = socket.socket()
    sock.settimeout(0.2)
    try:
        assert sock.connect_ex(("127.0.0.1", 8000)) != 0
    finally:
        sock.close()


def main() -> None:
    assert_workflow_complete()
    assert_docs_complete()
    assert_openapi_contract()
    assert_task_blocked_contract()
    assert_cloud_blockers()
    print("zhixing api contract validation ok")


if __name__ == "__main__":
    main()
