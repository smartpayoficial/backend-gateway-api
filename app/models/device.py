from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from .enrolment import Enrolment


class DeviceState(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    # Agrega otros estados si los necesitas


class DeviceBase(BaseModel):
    name: str
    imei: str
    imei_two: str
    serial_number: str
    model: str
    brand: str
    product_name: str
    state: DeviceState = DeviceState.ACTIVE


class DeviceCreate(DeviceBase):
    enrolment_id: UUID


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    imei: Optional[str] = None
    imei_two: Optional[str] = None
    serial_number: Optional[str] = None
    model: Optional[str] = None
    brand: Optional[str] = None
    product_name: Optional[str] = None
    state: Optional[DeviceState] = None
    enrolment_id: Optional[UUID] = None


class Device(BaseModel):
    device_id: UUID
    name: str
    imei: str
    imei_two: Optional[str] = None
    serial_number: str
    model: str
    brand: str
    product_name: str
    state: str
    enrolment: Optional[Enrolment] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",  # Ignore extra fields
        arbitrary_types_allowed=True,  # Allow arbitrary types
    )


class DeviceDB(DeviceBase):
    @field_validator("state", mode="before")
    @classmethod
    def normalize_state(cls, v):
        if isinstance(v, str):
            v = v.capitalize()
            if v not in ("Active", "Inactive"):
                raise ValueError(f"Estado desconocido: {v}")
            return v
        return v

    device_id: UUID
    enrolment_id: UUID

    model_config = ConfigDict(from_attributes=True)
