from typing import Optional

from pydantic import BaseModel


class RoleOut(BaseModel):
    role_id: str
    name: str
    description: str


class UserOut(BaseModel):
    user_id: str
    city: dict | None = None
    dni: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    second_last_name: Optional[str] = None
    email: str
    prefix: str
    phone: str
    address: str
    username: str
    state: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    role: RoleOut


class UserUpdate(BaseModel):
    city_id: Optional[str] = None
    dni: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    second_last_name: Optional[str] = None
    email: Optional[str] = None
    prefix: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[str] = None
    state: Optional[str] = None
