from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime
from .account_type import AccountTypeDB

# --------- SCHEMAS ---------
class StoreContactBase(BaseModel):
    contact_details: Dict[str, Any]
    description: Optional[str] = None


class StoreContactCreate(StoreContactBase):
    store_id: UUID
    contact_details: Dict[str, Any]
    description: Optional[str] = None
    account_type_id: int


class StoreContactUpdate(BaseModel):
    contact_details: Dict[str, Any]
    description: Optional[str] = None
    account_type_id: int


class StoreContactDB(StoreContactBase):
    id: UUID = Field(alias="contact_id") # Mapea el campo 'contact_id' de la DB a 'id' en el modelo
    store_id: UUID
    account_type_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class StoreContactOut(StoreContactDB):
    account_type: AccountTypeDB

    class Config:
        from_attributes = True
        populate_by_name = True
