from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class FactoryResetProtectionState(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class FactoryResetProtectionBase(BaseModel):
    account_id: str
    name: str
    email: str
    state: FactoryResetProtectionState


class FactoryResetProtectionCreate(FactoryResetProtectionBase):
    pass


class FactoryResetProtectionUpdate(BaseModel):
    name: Optional[str] = None
    state: Optional[FactoryResetProtectionState] = None


class FactoryResetProtectionInDB(FactoryResetProtectionBase):
    factory_reset_protection_id: UUID

    class Config:
        orm_mode = True


class FactoryResetProtectionResponse(FactoryResetProtectionInDB):
    pass
