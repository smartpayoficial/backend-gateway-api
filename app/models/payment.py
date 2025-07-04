from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .device import Device
from .plan import Plan


class PaymentState(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    FAILED = "Failed"
    RETURNED = "Returned"


class PlanBase(BaseModel):
    user_id: UUID
    vendor_id: UUID
    device_id: UUID
    initial_date: date
    quotas: int
    contract: str


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    user_id: Optional[UUID] = None
    vendor_id: Optional[UUID] = None
    device_id: Optional[UUID] = None
    initial_date: Optional[date] = None
    quotas: Optional[int] = None
    contract: Optional[str] = None


class PlanDB(PlanBase):
    plan_id: UUID

    model_config = ConfigDict(from_attributes=True)


class Payment(BaseModel):
    payment_id: UUID
    value: Decimal
    method: str
    state: PaymentState
    date: datetime
    reference: str
    device: Device
    plan: Plan

    model_config = ConfigDict(from_attributes=True)


class PaymentCreate(BaseModel):
    value: Decimal
    method: str
    state: PaymentState
    date: datetime
    reference: str
    device_id: UUID
    plan_id: UUID


class PaymentUpdate(BaseModel):
    device_id: Optional[UUID] = None
    plan_id: Optional[UUID] = None
    value: Optional[Decimal] = None
    method: Optional[str] = None
    state: Optional[PaymentState] = None
    date: Optional[datetime] = None
    reference: Optional[str] = None
