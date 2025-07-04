from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

# Simplified models for nested objects in payment responses


class PaymentDeviceResponse(BaseModel):
    """Simplified Device model for payment responses"""

    device_id: UUID
    serial: Optional[str] = None
    model: Optional[str] = None
    vendor_id: Optional[UUID] = None
    enrolment_id: Optional[UUID] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        arbitrary_types_allowed=True,
    )


class PaymentUserResponse(BaseModel):
    """Simplified User model for payment responses"""

    user_id: UUID
    name: Optional[str] = None
    email: Optional[str] = None
    role_id: Optional[UUID] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        arbitrary_types_allowed=True,
    )


class PaymentPlanResponse(BaseModel):
    """Simplified Plan model for payment responses"""

    plan_id: UUID
    user_id: UUID
    vendor_id: UUID
    device_id: UUID
    initial_date: Optional[date] = None
    quotas: Optional[int] = None
    contract: Optional[str] = None
    user: Optional[PaymentUserResponse] = None
    vendor: Optional[PaymentUserResponse] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        arbitrary_types_allowed=True,
    )


class PaymentResponse(BaseModel):
    """Payment model for API responses"""

    payment_id: UUID
    value: Decimal
    method: str
    state: str
    date: datetime
    reference: str
    device_id: Optional[UUID] = None
    plan_id: Optional[UUID] = None
    device: Optional[PaymentDeviceResponse] = None
    plan: Optional[PaymentPlanResponse] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        arbitrary_types_allowed=True,
    )
