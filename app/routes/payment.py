from typing import List, Optional
from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, Query, Response, status

from app.models.payment import PaymentCreate, PaymentState, PaymentUpdate
from app.models.payment_response import PaymentResponse
from app.services import payment as payment_service

router = APIRouter(tags=["payments"])


@router.post("/", response_model=PaymentResponse)
async def create_payment(payment: PaymentCreate):
    new_payment = await payment_service.create_payment(payment)
    if not new_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment could not be created.",
        )
    return new_payment


@router.get("/", response_model=List[PaymentResponse])
async def get_payments(
    state: Optional[PaymentState] = Query(None),
    plan_id: Optional[UUID] = Query(None),
    device_id: Optional[UUID] = Query(None),
):
    try:
        return await payment_service.get_payments(
            state=state, plan_id=plan_id, device_id=device_id
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from downstream service: {e.response.text}",
        )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: UUID):
    payment = await payment_service.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.patch("/{payment_id}", response_model=PaymentResponse)
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
