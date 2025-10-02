from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, Field

class AccountTypeBase(BaseModel):
    name: str
    description: Optional[str] = None

class AccountTypeCreate(AccountTypeBase):
    country_id: UUID

class AccountTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class AccountTypeDB(BaseModel):
    account_type_id: int = Field(..., alias="id")
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    is_international: Optional[bool] = False
    form_schema: Optional[List[Any]] = None
    category: str
    country_id: Optional[UUID] = None

    class Config:
        orm_mode = True
        populate_by_name = True
