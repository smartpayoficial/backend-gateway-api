from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.models.payment import PaymentCreate, PaymentDB, PaymentState, PaymentUpdate
from app.servicios import payment as payment_service

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=PaymentDB)
async def create_payment(payment: PaymentCreate):
    return await payment_service.create_payment(payment)


@router.get("/", response_model=List[PaymentDB])
async def get_payments(state: Optional[PaymentState] = Query(None)):
    return await payment_service.get_payments(state)


@router.get("/{payment_id}", response_model=PaymentDB)
async def get_payment(payment_id: UUID):
    payment = await payment_service.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.patch("/{payment_id}", response_model=PaymentDB)
async def update_payment(payment_id: UUID, payment: PaymentUpdate):
    updated = await payment_service.update_payment(payment_id, payment)
    if not updated:
        raise HTTPException(status_code=404, detail="Payment not found or not updated")
    return updated


@router.delete("/{payment_id}", response_model=bool)
async def delete_payment(payment_id: UUID):
    deleted = await payment_service.delete_payment(payment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Payment not found or not deleted")
    return deleted
