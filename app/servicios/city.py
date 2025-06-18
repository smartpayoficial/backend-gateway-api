import os
from typing import List, Optional
from uuid import UUID

import httpx

from app.models.city import CityCreate, CityDB, CityUpdate

DB_SVC_URL = os.getenv("USER_SVC_URL") or os.getenv("DB_API", "http://localhost:8002")
CITY_API_PREFIX = "/api/v1"
INTERNAL_HDR = {"X-Internal-Request": "true"}

# CRUD Functions for City entity


async def get_city(city_id: UUID) -> Optional[CityDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{CITY_API_PREFIX}/cities/{city_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        return CityDB(**resp.json())
    return None


async def get_cities() -> List[CityDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{CITY_API_PREFIX}/cities"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        return [CityDB(**item) for item in resp.json()]
    return []


async def create_city(city: CityCreate) -> CityDB:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{CITY_API_PREFIX}/cities"
        resp = await client.post(
            url, headers=INTERNAL_HDR, json=city.model_dump(mode="json")
        )
    resp.raise_for_status()
    return CityDB(**resp.json())


async def update_city(city_id: UUID, city: CityUpdate) -> Optional[CityDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{CITY_API_PREFIX}/cities/{city_id}"
        resp = await client.patch(
            url, headers=INTERNAL_HDR, json=city.dict(exclude_none=True)
        )
    if resp.status_code == 204:
        return None
    resp.raise_for_status()
    return CityDB(**resp.json())


async def delete_city(city_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{CITY_API_PREFIX}/cities/{city_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)
    return resp.status_code == 204
