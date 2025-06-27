from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from tortoise import fields
from tortoise.models import Model


# Database Models (Tortoise ORM)
class Country(Model):
    country_id = fields.UUIDField(pk=True)
    code = fields.SmallIntField(unique=True)
    name = fields.CharField(max_length=80, unique=True)
    prefix = fields.CharField(max_length=4)

    class Meta:
        table = "country"


class Region(Model):
    region_id = fields.UUIDField(pk=True)
    country = fields.ForeignKeyField("models.Country", related_name="regions")
    name = fields.CharField(max_length=80)

    class Meta:
        table = "region"


class City(Model):
    city_id = fields.UUIDField(pk=True)
    region = fields.ForeignKeyField("models.Region", related_name="cities")
    name = fields.CharField(max_length=80)

    class Meta:
        table = "city"


class Location(Model):
    location_id = fields.UUIDField(pk=True)
    device = fields.ForeignKeyField("models.Device", related_name="locations")
    latitude = fields.FloatField()
    longitude = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "location"

    def __str__(self):
        return f"Location for device {self.device_id} at {self.created_at}"


# Pydantic Schemas


# Schemas for Country
class CountryBase(BaseModel):
    code: int
    name: str
    prefix: str


class CountryCreate(CountryBase):
    pass


class CountryUpdate(BaseModel):
    code: Optional[int] = None
    name: Optional[str] = None
    prefix: Optional[str] = None


class CountryDB(CountryBase):
    country_id: UUID

    class Config:
        from_attributes = True


# Schemas for Region
class RegionBase(BaseModel):
    name: str
    country_id: UUID


class RegionCreate(RegionBase):
    pass


class RegionUpdate(BaseModel):
    name: Optional[str] = None


class RegionDB(RegionBase):
    region_id: UUID
    country: Optional[CountryDB] = None

    class Config:
        from_attributes = True


# Schemas for City
class CityBase(BaseModel):
    name: str
    region_id: Optional[UUID] = None


class CityCreate(CityBase):
    pass


class CityUpdate(BaseModel):
    name: Optional[str] = None
    region_id: Optional[UUID] = None


class CityDB(CityBase):
    city_id: UUID
    region: Optional[RegionDB] = None

    class Config:
        from_attributes = True


# Schemas for Location
class LocationBase(BaseModel):
    device_id: UUID
    latitude: float
    longitude: float


class LocationCreate(LocationBase):
    pass


class LocationDB(LocationBase):
    location_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
