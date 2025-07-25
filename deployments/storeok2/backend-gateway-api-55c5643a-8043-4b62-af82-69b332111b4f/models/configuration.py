from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ConfigurationBase(BaseModel):
    key: str
    value: str
    description: str


class ConfigurationCreate(ConfigurationBase):
    pass


class ConfigurationUpdate(BaseModel):
    key: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None


class ConfigurationDB(ConfigurationBase):
    configuration_id: UUID

    class Config:
        orm_mode = True
