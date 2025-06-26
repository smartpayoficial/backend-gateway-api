from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.models.payment import Payment, PaymentCreate, PaymentState, PaymentUpdate
from app.servicios import payment as payment_service

router = APIRouter(tags=["payments"])


@router.post("/", response_model=Payment)
async def create_payment(payment: PaymentCreate):
    return await payment_service.create_payment(payment)


@router.get("/", response_model=List[Payment])
async def get_payments(
    state: Optional[PaymentState] = Query(None),
    plan_id: Optional[UUID] = Query(None),
):
    return await payment_service.get_payments(state=state, plan_id=plan_id)


@router.get("/{payment_id}", response_model=Payment)
async def get_payment(payment_id: UUID):
    payment = await payment_service.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.patch("/{payment_id}", response_model=Payment)
async def update_payment(payment_id: UUID, payment: PaymentUpdate):
    updated = await payment_service.update_payment(payment_id, payment)
    if not updated:
        raise HTTPException(status_code=404, detail="Payment not found or not updated")
    return updated


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(payment_id: UUID):
    deleted = await payment_service.delete_payment(payment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Payment not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
