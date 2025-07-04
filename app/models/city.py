from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CityBase(BaseModel):
    name: str
    region_id: Optional[UUID] = None


class CityCreate(CityBase):
    pass


class CityUpdate(CityBase):
    pass


class CityDB(CityBase):
    city_id: UUID
    model_config = ConfigDict(from_attributes=True)
