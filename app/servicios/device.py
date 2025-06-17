import os
from typing import List, Optional
from uuid import UUID

import httpx

from app.models.device import DeviceCreate, DeviceDB, DeviceUpdate

USER_SVC_URL = os.getenv("USER_SVC_URL") or os.getenv("DB_API", "http://localhost:8002")
DEVICE_API_PREFIX = "/api/v1"
INTERNAL_HDR = {"X-Internal-Request": "true"}

# CRUD Functions for Device entity


async def get_device(device_id: UUID) -> Optional[DeviceDB]:
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{DEVICE_API_PREFIX}/devices/{device_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        return DeviceDB(**resp.json())
    return None


async def get_devices() -> List[DeviceDB]:
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{DEVICE_API_PREFIX}/devices"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        return [DeviceDB(**item) for item in resp.json()]
    return []


async def create_device(device: DeviceCreate) -> DeviceDB:
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{DEVICE_API_PREFIX}/devices"
        resp = await client.post(
            url, headers=INTERNAL_HDR, json=device.model_dump(mode="json")
        )
    resp.raise_for_status()
    return DeviceDB(**resp.json())


async def update_device(device_id: UUID, device: DeviceUpdate) -> Optional[DeviceDB]:
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{DEVICE_API_PREFIX}/devices/{device_id}"
        resp = await client.patch(
            url, headers=INTERNAL_HDR, json=device.dict(exclude_none=True)
        )
    if resp.status_code == 204:
        return None
    resp.raise_for_status()
    return DeviceDB(**resp.json())


async def delete_device(device_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{DEVICE_API_PREFIX}/devices/{device_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)
    return resp.status_code == 204
