from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from .city import CityDB
from .role import Role
from .store import StoreDB


# Simplified store model for user response
class StoreResponse(BaseModel):
    id: UUID
    nombre: str
    country_id: Optional[UUID] = None
    plan: Optional[str] = None
    tokens_disponibles: Optional[int] = None
    back_link: Optional[str] = None
    db_link: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        arbitrary_types_allowed=True,
    )


class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dni: Optional[str] = None

    middle_name: Optional[str] = None
    second_last_name: Optional[str] = None
    prefix: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    # A = Active, I = Initial
    state: Optional[str] = "A"


class UserCreate(UserBase):
    city_id: Optional[UUID] = None
    role_id: Optional[UUID] = None
    store: Optional[UUID] = None
    password: str

    @field_validator("city_id", "role_id", "store", mode="before")
    @classmethod
    def to_uuid(cls, v):
        if isinstance(v, str):
            return UUID(v)
        return v


class UserUpdate(BaseModel):
    city_id: Optional[UUID] = None
    dni: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    second_last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    prefix: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[UUID] = None
    store: Optional[UUID] = None
    state: Optional[str] = None


class User(UserBase):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",  # Ignore extra fields
        arbitrary_types_allowed=True,  # Allow arbitrary types
    )

    user_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    role: Optional[Role] = None
    city: Optional[CityDB] = None
    store: Optional[StoreResponse] = None


class UserPaymentResponse(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    second_last_name: Optional[str] = None
