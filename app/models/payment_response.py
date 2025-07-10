from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

# Simplified models for nested objects in payment responses


class PaymentDeviceResponse(BaseModel):
     """Modelo simplificado de Device"""
     device_id: UUID
     name: Optional[str] = None
     imei: str
     imei_two: Optional[str] = None
     serial_number: Optional[str] = None
     model: Optional[str] = None
     brand: str
     product_name: str
     vendor_id: Optional[UUID] = None
     enrolment_id: Optional[UUID] = None

     model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
     )


class PaymentUserResponse(BaseModel):
    """Simplified User model for payment responses"""

    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    second_last_name: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )


class PaymentPlanResponse(BaseModel):
    """Modelo simplificado de Plan en el contexto de un pago"""
    plan_id: UUID
    user_id: UUID
    vendor_id: UUID
    device_id: UUID
    initial_date: Optional[date] = None
    quotas: Optional[int] = None
    contract: Optional[str] = None
    user: Optional[PaymentUserResponse] = None
    vendor: Optional[PaymentUserResponse] = None
    device: Optional[PaymentDeviceResponse] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )


class PaymentResponse(BaseModel):
    """Modelo final de respuesta de pago"""
    payment_id: UUID
    value: Decimal
    method: str
    state: str
    date: datetime
    reference: str
    plan: Optional[PaymentPlanResponse] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )
