from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/commerce", tags=["commerce"])


class CartItem(BaseModel):
    product_id: str
    quantity: int = Field(1, ge=1)


class CheckoutRequest(BaseModel):
    user_id: uuid.UUID
    items: list[CartItem] = Field(default_factory=list)


@router.get("/status")
async def commerce_status():
    return {
        "provider": "Medusa",
        "status": "placeholder",
        "detail": "Medusa is planned for P4 and is not running in Cloud.",
    }


@router.post("/checkout")
async def checkout(body: CheckoutRequest):
    return {
        "order_id": str(uuid.uuid4()),
        "user_id": str(body.user_id),
        "items": [item.model_dump() for item in body.items],
        "status": "draft",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/wallet/{user_id}")
async def wallet(user_id: uuid.UUID):
    return {
        "user_id": str(user_id),
        "balance": 0,
        "currency": "CNY",
        "status": "placeholder",
    }
