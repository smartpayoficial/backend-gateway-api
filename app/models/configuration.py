from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ConfigurationBase(BaseModel):
    key: str
    value: str
    description: str
    store_id: Optional[UUID] = None


class ConfigurationCreate(ConfigurationBase):
    pass


class ConfigurationUpdate(BaseModel):
    key: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None
    store_id: Optional[UUID] = None


class ConfigurationDB(ConfigurationBase):
    configuration_id: UUID

    class Config:
        orm_mode = True
