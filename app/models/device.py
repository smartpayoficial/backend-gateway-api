from enum import Enum
from uuid import UUID

from pydantic import BaseModel, field_validator


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


class DeviceUpdate(DeviceBase):
    pass


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

    class Config:
        orm_mode = True
