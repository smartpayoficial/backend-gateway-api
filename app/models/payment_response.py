from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

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
    user_id: Optional[UUID] = None
    vendor_id: Optional[UUID] = None
    device_id: Optional[UUID] = None
    initial_date: Optional[date] = None
    value: Optional[Decimal] = None
    quotas: Optional[int] = None
    period: Optional[int] = None
    contract: Optional[str] = None
    
    # Campos anidados como diccionarios para mantener estructura completa
    user: dict = Field(default_factory=dict)
    vendor: dict = Field(default_factory=dict)
    device: dict = Field(default_factory=dict)

    model_config = ConfigDict(
        from_attributes=True,
        extra="allow"  # Permitir campos adicionales
    )


class PaymentResponse(BaseModel):
    """Modelo final de respuesta de pago"""
    payment_id: UUID
    value: Decimal
    method: str
    state: str
    date: datetime
    reference: str
    plan: Optional[PaymentPlanResponse] = Field(default=None, exclude=False)

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v),
            UUID: lambda v: str(v)
        },
        extra="allow"
    )

    def dict(self, **kwargs):
        # Forzar inclusión de todos los campos al serializar
        kwargs.setdefault('exclude_none', False)
        kwargs.setdefault('exclude_unset', False)
        return super().dict(**kwargs)
