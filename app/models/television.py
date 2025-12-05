from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from .enrolment import Enrolment


class TelevisionState(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    # Agrega otros estados si los necesitas


class TelevisionBase(BaseModel):
    brand: str
    model: str
    android_version: int
    serial_number: str
    board: str
    fingerprint: str
    state: TelevisionState = (TelevisionState.ACTIVE) 


class TelevisionCreate(TelevisionBase):
    enrolment_id: UUID


class TelevisionUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    android_version: Optional[int] = None
    serial_number: Optional[str] = None
    board: Optional[str] = None
    fingerprint: Optional[str] = None
    state: Optional[TelevisionState] = None
    enrolment_id: Optional[UUID] = None

class Television(BaseModel):
    television_id: UUID
    brand: str
    model: str
    android_version: int
    serial_number: str
    board: str
    fingerprint: str
    state: Optional[str] = None
    enrolment: Optional[Enrolment] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",  # Ignore extra fields
        arbitrary_types_allowed=True,  # Allow arbitrary types
    )


class TelevisionDB(TelevisionBase):
    @field_validator("state", mode="before")
    @classmethod
    def normalize_state(cls, v):
        if isinstance(v, str):
            v = v.capitalize()
            if v not in ("Active", "Inactive"):
                raise ValueError(f"Estado desconocido: {v}")
            return v
        return v

    television_id: UUID
    enrolment_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
