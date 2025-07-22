import os
from typing import List, Optional
from uuid import UUID
import logging

import httpx

from app.models.payment import PaymentCreate, PaymentState, PaymentUpdate
from app.models.payment_response import PaymentResponse

USER_SVC_URL = os.getenv("USER_SVC_URL", "http://localhost:8002")
PAYMENT_API_URL = f"{USER_SVC_URL}/api/v1/payments"

logging.basicConfig(level=logging.DEBUG)

async def create_payment(payment_in: PaymentCreate) -> Optional[PaymentResponse]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            PAYMENT_API_URL, json=payment_in.model_dump(mode="json")
        )
        if response.status_code == 201:
            return PaymentResponse(**response.json())
        return None


async def get_payments(
    state: Optional[PaymentState] = None,
    plan_id: Optional[UUID] = None,
    device_id: Optional[UUID] = None
) -> List[PaymentResponse]:
    params = {}
    if state:
        params["state"] = state.value
    if plan_id:
        params["plan_id"] = str(plan_id)
    if device_id:
        params["device_id"] = str(device_id)

    async with httpx.AsyncClient() as client:
        response = await client.get(PAYMENT_API_URL, params=params)
        response.raise_for_status()
        
        raw_data = response.json()
        
        payments = []
        for item in raw_data:
            if 'plan' not in item or not item['plan']:
                item['plan'] = None
            else:
                plan_data = item['plan']
                if 'plan_id' not in plan_data:
                    item['plan'] = None
                else:
                    # Asegurar estructura básica
                    plan_data.setdefault('user', {})
                    plan_data.setdefault('vendor', {})
                    plan_data.setdefault('device', {})
                    
                    # Asignar IDs desde los objetos anidados si existen
                    if 'user' in plan_data and 'user_id' in plan_data['user']:
                        plan_data['user_id'] = plan_data['user']['user_id']
                    if 'vendor' in plan_data and 'user_id' in plan_data['vendor']:
                        plan_data['vendor_id'] = plan_data['vendor']['user_id']
                    if 'device' in plan_data and 'device_id' in plan_data['device']:
                        plan_data['device_id'] = plan_data['device']['device_id']
            
            payments.append(PaymentResponse(**item))
        
        return payments


async def get_payment(payment_id: UUID) -> Optional[PaymentResponse]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PAYMENT_API_URL}/{payment_id}")
        if response.status_code == 200:
            return PaymentResponse(**response.json())
        return None


async def update_payment(
    payment_id: UUID, payment_update: PaymentUpdate
) -> Optional[PaymentResponse]:
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{PAYMENT_API_URL}/{payment_id}",
            json=payment_update.model_dump(exclude_unset=False, mode="json"),
        )
        if response.status_code == 200:
            return PaymentResponse(**response.json())
        return None


async def delete_payment(payment_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{PAYMENT_API_URL}/{payment_id}")
        return response.status_code == 204
