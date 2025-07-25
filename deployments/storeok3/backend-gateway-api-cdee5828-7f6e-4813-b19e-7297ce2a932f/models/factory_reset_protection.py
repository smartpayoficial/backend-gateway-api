from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FactoryResetProtectionResponse(FactoryResetProtectionInDB):
    pass
