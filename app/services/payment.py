import os
from typing import List, Optional
from uuid import UUID

import httpx
from app.models.payment import Payment, PaymentCreate, PaymentState, PaymentUpdate

USER_SVC_URL = os.getenv("USER_SVC_URL", "http://localhost:8002")
PAYMENT_API_URL = f"{USER_SVC_URL}/api/v1/payments"


async def create_payment(payment_in: PaymentCreate) -> Optional[Payment]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            PAYMENT_API_URL, json=payment_in.model_dump(mode="json")
        )
        if response.status_code == 201:
            return Payment(**response.json())
        return None


async def get_payments(
    state: Optional[PaymentState] = None, plan_id: Optional[UUID] = None
) -> List[Payment]:
    params = {}
    if state:
        params["state"] = state.value
    if plan_id:
        params["plan_id"] = str(plan_id)

    async with httpx.AsyncClient() as client:
        response = await client.get(PAYMENT_API_URL, params=params)
        response.raise_for_status()
        return [Payment(**item) for item in response.json()]


async def get_payment(payment_id: UUID) -> Optional[Payment]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PAYMENT_API_URL}/{payment_id}")
        if response.status_code == 200:
            return Payment(**response.json())
        return None


async def update_payment(
    payment_id: UUID, payment_update: PaymentUpdate
) -> Optional[Payment]:
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{PAYMENT_API_URL}/{payment_id}",
            json=payment_update.model_dump(mode="json", exclude_unset=True),
        )
        if response.status_code == 200:
            return Payment(**response.json())
        return None


async def delete_payment(payment_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{PAYMENT_API_URL}/{payment_id}")
        return response.status_code == 204
