"""MetaGPT-X HTTP client for 知行."""
from __future__ import annotations

import os
from typing import Any, AsyncIterator, Optional

import httpx

DEFAULT_BASE = os.getenv("METAGPT_X_API", "http://127.0.0.1:8000")


class MetaGPTBridgeError(Exception):
    pass


class MetaGPTClient:
    def __init__(self, base_url: str | None = None, timeout: float = 120.0):
        self.base_url = (base_url or DEFAULT_BASE).rstrip("/")
        self.timeout = timeout

    async def health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(f"{self.base_url}/api/v1/health")
            r.raise_for_status()
            return r.json()

    async def queue_status(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(f"{self.base_url}/api/v1/queue")
            r.raise_for_status()
            return r.json()

    async def create_sop_project(
        self,
        name: str,
        idea: str,
        *,
        investment: float = 5.0,
        n_round: int = 8,
        run_tests: bool = True,
        skip_dev: bool = False,
        auto_approve: bool = True,
    ) -> dict[str, Any]:
        payload = {
            "name": name,
            "idea": idea,
            "investment": investment,
            "n_round": n_round,
            "run_tests": run_tests,
            "skip_dev": skip_dev,
            "auto_approve": auto_approve,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self.base_url}/api/v1/projects/sop", json=payload)
            if r.status_code >= 400:
                raise MetaGPTBridgeError(f"SOP create failed: {r.status_code} {r.text}")
            return r.json()

    async def get_project(self, job_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(f"{self.base_url}/api/v1/projects/{job_id}")
            r.raise_for_status()
            return r.json()

    async def list_projects(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(f"{self.base_url}/api/v1/projects")
            r.raise_for_status()
            data = r.json()
            return data if isinstance(data, list) else data.get("items", [])

    async def optimize(self, job_id: str, qa_fix_rounds: int = 3) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/api/v1/projects/{job_id}/optimize",
                json={"qa_fix_rounds": qa_fix_rounds, "use_aider": True},
            )
            r.raise_for_status()
            return r.json()

    async def stream_logs_ws(self, job_id: str) -> AsyncIterator[str]:
        """Yield log lines from MetaGPT-X WebSocket (best-effort)."""
        import websockets

        url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{url}/api/v1/projects/{job_id}/ws"
        async with websockets.connect(ws_url) as ws:
            async for message in ws:
                yield message
