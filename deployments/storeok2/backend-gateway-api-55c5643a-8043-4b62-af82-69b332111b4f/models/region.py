from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .country import CountryDB


class RegionBase(BaseModel):
    name: str
    country_id: Optional[UUID] = None


class RegionCreate(RegionBase):
    pass


class RegionUpdate(BaseModel):
    name: Optional[str] = None
    country_id: Optional[UUID] = None


class RegionDB(RegionBase):
    region_id: UUID
    country: Optional[CountryDB] = None
    model_config = ConfigDict(from_attributes=True)
