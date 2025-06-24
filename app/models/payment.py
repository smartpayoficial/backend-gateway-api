from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


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

    class Config:
        orm_mode = True


class PaymentBase(BaseModel):
    device_id: UUID
    plan_id: UUID
    value: Decimal
    method: str
    state: PaymentState
    date: datetime
    reference: str


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    device_id: Optional[UUID] = None
    plan_id: Optional[UUID] = None
    value: Optional[Decimal] = None
    method: Optional[str] = None
    state: Optional[PaymentState] = None
    date: Optional[datetime] = None
    reference: Optional[str] = None


class PaymentDB(PaymentBase):
    payment_id: UUID

    class Config:
        orm_mode = True
