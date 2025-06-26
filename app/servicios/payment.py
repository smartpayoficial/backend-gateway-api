import os
from typing import List, Optional
from uuid import UUID

import httpx

from app.models.payment import Payment, PaymentCreate, PaymentState, PaymentUpdate

DB_SVC_URL = os.getenv("USER_SVC_URL") or os.getenv("DB_API", "http://localhost:8002")
PAYMENT_API_PREFIX = "/api/v1/payments"
INTERNAL_HDR = {"X-Internal-Request": "true"}

# CRUD Functions for Payment entity


async def create_payment(payment: PaymentCreate) -> Payment:
    # The DB service expects a flat structure with IDs, not nested objects.
    # We convert the main object to a dict, excluding the nested objects.
    payment_data = payment.model_dump(mode="json", exclude={"device", "plan"})

    # Then, we add the IDs from the nested objects.
    payment_data["device_id"] = str(payment.device.device_id)
    payment_data["plan_id"] = str(payment.plan.plan_id)

    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{PAYMENT_API_PREFIX}"
        resp = await client.post(url, headers=INTERNAL_HDR, json=payment_data)
    resp.raise_for_status()
    return Payment(**resp.json())


async def get_payment(payment_id: UUID) -> Optional[Payment]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{PAYMENT_API_PREFIX}/{payment_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        return Payment(**resp.json())
    return None


async def get_payments(
    state: Optional[PaymentState] = None, plan_id: Optional[UUID] = None
) -> List[Payment]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{PAYMENT_API_PREFIX}"
        params = {}
        if state:
            params["state"] = state.value
        if plan_id:
            params["plan_id"] = str(plan_id)

        resp = await client.get(url, headers=INTERNAL_HDR, params=params or None)
    if resp.status_code == 200:
        return [Payment(**item) for item in resp.json()]
    return []


async def update_payment(payment_id: UUID, payment: PaymentUpdate) -> Optional[Payment]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{PAYMENT_API_PREFIX}/{payment_id}"
        resp = await client.patch(
            url, headers=INTERNAL_HDR, json=payment.dict(exclude_none=True)
        )
    if resp.status_code == 204:
        return None
    resp.raise_for_status()
    return Payment(**resp.json())


async def delete_payment(payment_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{PAYMENT_API_PREFIX}/{payment_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)
    return resp.status_code == 204
