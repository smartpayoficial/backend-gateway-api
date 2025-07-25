from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CountryBase(BaseModel):
    name: str
    code: str


class CountryCreate(CountryBase):
    pass


class CountryUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None


class CountryDB(CountryBase):
    country_id: Optional[UUID] = None

    class Config:
        orm_mode = True
