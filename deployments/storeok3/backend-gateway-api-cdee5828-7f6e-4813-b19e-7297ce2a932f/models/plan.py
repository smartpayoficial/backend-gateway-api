from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .device import DeviceDB
from .user import UserPaymentResponse


class PlanBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    period: Optional[int] = None
    active: bool = True


class PlanCreate(BaseModel):
    user_id: UUID
    vendor_id: UUID
    device_id: UUID
    initial_date: str = Field(description="Date in ISO 8601 format (YYYY-MM-DD)")
    value: Decimal
    quotas: int
    period: int
    contract: str

    @field_validator("initial_date")
    @classmethod
    def validate_date_format(cls, v):
        # Check if the date is in ISO 8601 format (YYYY-MM-DD)
        try:
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError(
                'initial_date must be in ISO 8601 format (YYYY-MM-DD), e.g., "2025-07-04"'
            )


class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    value: Decimal
    period: Optional[int] = None
    active: Optional[bool] = None


class Plan(PlanBase):
    user_id: UUID
    vendor_id: UUID
    device_id: UUID
    initial_date: date
    quotas: int
    period: int
    contract: str
    plan_id: UUID
    user: Optional[UserPaymentResponse] = None
    vendor: Optional[UserPaymentResponse] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",  # Ignore extra fields
        arbitrary_types_allowed=True,  # Allow arbitrary types
    )


class PlanDB(BaseModel):
    user_id: UUID
    vendor_id: UUID
    device_id: UUID
    initial_date: str = Field(description="Date in ISO 8601 format (YYYY-MM-DD)")
    quotas: int
    period: int
    contract: str
    plan_id: UUID

    # For backward compatibility
    @property
    def id(self) -> UUID:
        return self.plan_id

    @field_validator("initial_date")
    @classmethod
    def validate_date_format(cls, v):
        # Check if the date is in ISO 8601 format (YYYY-MM-DD)
        try:
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError(
                'initial_date must be in ISO 8601 format (YYYY-MM-DD), e.g., "2025-07-04"'
            )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PlanRaw(BaseModel):
    user_id: UUID
    vendor_id: UUID
    device_id: UUID
    initial_date: str
    quotas: int
    period: int
    value: Decimal
    contract: str
    plan_id: UUID
    user: Optional[UserPaymentResponse] = None
    vendor: Optional[UserPaymentResponse] = None
    device: Optional[DeviceDB] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",  # Ignore extra fields
        arbitrary_types_allowed=True,  # Allow arbitrary types
    )
