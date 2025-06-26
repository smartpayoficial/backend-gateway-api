from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from .role import Role


class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    dni: str
    city_id: UUID
    role_id: UUID
    middle_name: Optional[str] = None
    second_last_name: Optional[str] = None
    prefix: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    state: Optional[str] = "A"


class UserCreate(UserBase):
    password: str


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
    state: Optional[str] = None


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    created_at: datetime
    updated_at: datetime
    role: Role
