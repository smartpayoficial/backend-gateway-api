import os
from typing import List, Optional
from uuid import UUID

import httpx

from app.models.location import (
    CityCreate,
    CityDB,
    CityUpdate,
    CountryCreate,
    CountryDB,
    CountryUpdate,
    LocationCreate,
    LocationDB,
    RegionCreate,
    RegionDB,
    RegionUpdate,
)

DB_SVC_URL = os.getenv("USER_SVC_URL") or os.getenv("DB_API", "http://localhost:8002")
LOCATION_API_PREFIX = "/api/v1"
INTERNAL_HDR = {"X-Internal-Request": "true"}


# --- Country Service --- #


async def get_country(country_id: UUID) -> Optional[CountryDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/countries/{country_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    return CountryDB(**resp.json()) if resp.status_code == 200 else None


async def get_countries() -> List[CountryDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/countries/"
        resp = await client.get(url, headers=INTERNAL_HDR)
    return (
        [CountryDB(**country_data) for country_data in resp.json()]
        if resp.status_code == 200
        else []
    )


async def create_country(country_in: CountryCreate) -> CountryDB:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/countries/"
        resp = await client.post(
            url, headers=INTERNAL_HDR, json=country_in.model_dump(mode="json")
        )
    resp.raise_for_status()
    return CountryDB(**resp.json())


async def update_country(
    country_id: UUID, country_in: CountryUpdate
) -> Optional[CountryDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/countries/{country_id}"
        resp = await client.patch(
            url,
            headers=INTERNAL_HDR,
            json=country_in.model_dump(mode="json", exclude_none=True),
        )
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return CountryDB(**resp.json())


async def delete_country(country_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/countries/{country_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)
    return resp.status_code == 204


# --- Region Service --- #


async def get_region(region_id: UUID) -> Optional[RegionDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/regions/{region_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    return RegionDB(**resp.json()) if resp.status_code == 200 else None


async def get_regions() -> List[RegionDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/regions/"
        resp = await client.get(url, headers=INTERNAL_HDR)
    return (
        [RegionDB(**region_data) for region_data in resp.json()]
        if resp.status_code == 200
        else []
    )


async def create_region(region_in: RegionCreate) -> RegionDB:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/regions/"
        resp = await client.post(
            url, headers=INTERNAL_HDR, json=region_in.model_dump(mode="json")
        )
    resp.raise_for_status()
    return RegionDB(**resp.json())


async def update_region(region_id: UUID, region_in: RegionUpdate) -> Optional[RegionDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/regions/{region_id}"
        resp = await client.patch(
            url,
            headers=INTERNAL_HDR,
            json=region_in.model_dump(mode="json", exclude_none=True),
        )
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return RegionDB(**resp.json())


async def delete_region(region_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/regions/{region_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)
    return resp.status_code == 204


# --- City Service --- #


async def get_city(city_id: UUID) -> Optional[CityDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/cities/{city_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    return CityDB(**resp.json()) if resp.status_code == 200 else None


async def get_cities() -> List[CityDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/cities/"
        resp = await client.get(url, headers=INTERNAL_HDR)
    return (
        [CityDB(**city_data) for city_data in resp.json()]
        if resp.status_code == 200
        else []
    )


async def create_city(city_in: CityCreate) -> CityDB:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/cities/"
        resp = await client.post(
            url, headers=INTERNAL_HDR, json=city_in.model_dump(mode="json")
        )
    resp.raise_for_status()
    return CityDB(**resp.json())


async def update_city(city_id: UUID, city_in: CityUpdate) -> Optional[CityDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/cities/{city_id}"
        resp = await client.patch(
            url,
            headers=INTERNAL_HDR,
            json=city_in.model_dump(mode="json", exclude_none=True),
        )
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return CityDB(**resp.json())


async def delete_city(city_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/cities/{city_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)
    return resp.status_code == 204


# --- Location Service --- #


async def get_location(location_id: UUID) -> Optional[LocationDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/locations/{location_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    return LocationDB(**resp.json()) if resp.status_code == 200 else None


async def get_locations(device_id: Optional[UUID] = None) -> List[LocationDB]:
    params = {}
    if device_id:
        params["device_id"] = str(device_id)

    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/locations/"
        resp = await client.get(url, params=params, headers=INTERNAL_HDR)

    return (
        [LocationDB(**location) for location in resp.json()]
        if resp.status_code == 200
        else []
    )


async def create_location(location_in: LocationCreate) -> LocationDB:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/locations/"
        resp = await client.post(
            url, headers=INTERNAL_HDR, json=location_in.model_dump(mode="json")
        )
    resp.raise_for_status()
    return LocationDB(**resp.json())


async def delete_location(location_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{LOCATION_API_PREFIX}/locations/{location_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)
    return resp.status_code == 204
