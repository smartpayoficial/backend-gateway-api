from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .user import User


class PlanBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    active: bool = True


class PlanCreate(BaseModel):
    user_id: UUID
    vendor_id: UUID
    device_id: UUID
    initial_date: str  # formato YYYY-MM-DD
    quotas: int
    contract: str


class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    active: Optional[bool] = None


class Plan(PlanBase):
    plan_id: UUID
    user_id: UUID
    vendor_id: UUID
    device_id: UUID
    initial_date: date
    quotas: int
    contract: str
    user: User
    vendor: User

    class Config:
        from_attributes = True


class PlanDB(PlanBase):
    id: UUID

    class Config:
        orm_mode = True


class PlanRaw(BaseModel):
    user_id: UUID
    vendor_id: UUID
    device_id: UUID
    initial_date: str
    quotas: int
    contract: str
    plan_id: UUID
