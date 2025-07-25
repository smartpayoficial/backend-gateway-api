from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.country import CountryDB


class AdminDB(BaseModel):
    city_id: UUID
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
    password: str
    role_id: UUID
    state: str
    user_id: UUID
    role: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class StoreBase(BaseModel):
    nombre: str
    country_id: UUID
    tokens_disponibles: int = 0
    plan: str
    back_link: Optional[str] = None
    db_link: Optional[str] = None
    admin_id: Optional[UUID] = None  # Mantener compatibilidad


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    nombre: Optional[str] = None
    country_id: Optional[UUID] = None
    tokens_disponibles: Optional[int] = None
    plan: Optional[str] = None
    back_link: Optional[str] = None
    db_link: Optional[str] = None
    admin_id: Optional[UUID] = None  # Mantener compatibilidad


class StoreDB(StoreBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    country: Optional[CountryDB] = None
    admin: Optional[AdminDB] = None  # Entidad completa del admin
    
    # Mantener admin_id explícitamente para compatibilidad
    @property
    def admin_id(self) -> Optional[UUID]:
        return self.admin.user_id if self.admin else None
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
