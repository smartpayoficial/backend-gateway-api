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
