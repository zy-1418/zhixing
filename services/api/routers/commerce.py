from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from config import settings

router = APIRouter(prefix="/commerce", tags=["commerce"])


class CartCreateRequest(BaseModel):
    region_id: str | None = None
    email: str | None = None


class WalletAdjustRequest(BaseModel):
    user_id: str
    amount: int = Field(..., description="Amount in cents")
    reason: str


def _headers() -> dict[str, str]:
    if not settings.medusa_api_key:
        return {}
    return {"Authorization": f"Bearer {settings.medusa_api_key}"}


def _placeholder(kind: str) -> dict[str, Any]:
    return {
        "mode": "placeholder",
        "provider": "medusa",
        "kind": kind,
        "status": "skipped",
        "reason": "MEDUSA_API_KEY is not configured in this environment.",
    }


async def _get(path: str) -> dict[str, Any]:
    if not settings.medusa_api_key:
        return _placeholder(path)
    url = f"{settings.medusa_backend_url.rstrip('/')}/{path.lstrip('/')}"
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url, headers=_headers())
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


async def _post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    if not settings.medusa_api_key:
        result = _placeholder(path)
        result["payload"] = payload
        return result
    url = f"{settings.medusa_backend_url.rstrip('/')}/{path.lstrip('/')}"
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, headers=_headers(), json=payload)
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@router.get("/products")
async def list_products():
    return await _get("/store/products")


@router.post("/cart")
async def create_cart(body: CartCreateRequest):
    return await _post("/store/carts", body.model_dump(exclude_none=True))


@router.get("/orders")
async def list_orders():
    return await _get("/admin/orders")


@router.post("/wallet/adjust")
async def adjust_wallet(body: WalletAdjustRequest):
    return await _post("/admin/zhixing/wallet/adjust", body.model_dump())
