import os
from typing import List, Optional
from uuid import UUID

import httpx

from app.models.payment import PaymentCreate, PaymentDB, PaymentState, PaymentUpdate

DB_SVC_URL = os.getenv("USER_SVC_URL") or os.getenv("DB_API", "http://localhost:8002")
PAYMENT_API_PREFIX = "/api/v1/payments"
INTERNAL_HDR = {"X-Internal-Request": "true"}

# CRUD Functions for Payment entity


async def create_payment(payment: PaymentCreate) -> PaymentDB:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{PAYMENT_API_PREFIX}"
        resp = await client.post(
            url, headers=INTERNAL_HDR, json=payment.model_dump(mode="json")
        )
    resp.raise_for_status()
    return PaymentDB(**resp.json())


async def get_payment(payment_id: UUID) -> Optional[PaymentDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{PAYMENT_API_PREFIX}/{payment_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        return PaymentDB(**resp.json())
    return None


async def get_payments(state: Optional[PaymentState] = None) -> List[PaymentDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{PAYMENT_API_PREFIX}"
        params = {"state": state} if state else None
        resp = await client.get(url, headers=INTERNAL_HDR, params=params)
    if resp.status_code == 200:
        return [PaymentDB(**item) for item in resp.json()]
    return []


async def update_payment(
    payment_id: UUID, payment: PaymentUpdate
) -> Optional[PaymentDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{PAYMENT_API_PREFIX}/{payment_id}"
        resp = await client.patch(
            url, headers=INTERNAL_HDR, json=payment.dict(exclude_none=True)
        )
    if resp.status_code == 204:
        return None
    resp.raise_for_status()
    return PaymentDB(**resp.json())


async def delete_payment(payment_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{PAYMENT_API_PREFIX}/{payment_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)
    return resp.status_code == 204
