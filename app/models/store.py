from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.country import CountryDB


class StoreBase(BaseModel):
    nombre: str
    country_id: UUID
    tokens_disponibles: int = 0
    plan: str
    back_link: Optional[str] = None
    db_link: Optional[str] = None


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    nombre: Optional[str] = None
    country_id: Optional[UUID] = None
    tokens_disponibles: Optional[int] = None
    plan: Optional[str] = None
    back_link: Optional[str] = None
    db_link: Optional[str] = None


class StoreDB(StoreBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    country: Optional[CountryDB] = None

    class Config:
        orm_mode = True
