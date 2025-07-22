from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
import httpx

from app.models.payment_response import PaymentResponse
from app.services import payment as payment_service

router = APIRouter()

@router.get("/", response_model=List[PaymentResponse], status_code=status.HTTP_200_OK)
async def get_all_payments(
    state: Optional[str] = None,
    plan_id: Optional[UUID] = None,
    device_id: Optional[UUID] = None
):
    """
    Obtiene todos los pagos con filtros opcionales.
    Devuelve la estructura completa con detalles de plan, usuario, vendedor y dispositivo.
    """
    try:
        return await payment_service.get_payments(
            state=state,
            plan_id=plan_id,
            device_id=device_id
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from downstream service: {e.response.text}",
        )

@router.get("/{payment_id}", response_model=PaymentResponse, status_code=status.HTTP_200_OK)
async def get_payment_by_id(payment_id: UUID):
    """
    Obtiene un pago específico por su ID.
    Devuelve la estructura completa con detalles de plan, usuario, vendedor y dispositivo.
    """
    payment = await payment_service.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
