from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

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
    user_id: UUID
    vendor_id: UUID
    device_id: UUID
    initial_date: date
    quotas: int
    contract: str
    plan_id: UUID

    class Config:
        pass


class PlanDB(PlanBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class PlanRaw(BaseModel):
    user_id: UUID
    vendor_id: UUID
    device_id: UUID
    initial_date: str
    quotas: int
    contract: str
    plan_id: UUID
