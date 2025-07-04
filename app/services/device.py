import os
from typing import List, Optional
from uuid import UUID

import httpx
from app.models.device import Device, DeviceCreate, DeviceUpdate

USER_SVC_URL = os.getenv("USER_SVC_URL", "http://localhost:8002")


async def create_device(device_in: DeviceCreate) -> Optional[Device]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{USER_SVC_URL}/api/v1/devices/",
            json=device_in.model_dump(mode='json')
        )
        if response.status_code == 201:
            return Device(**response.json())
        return None


async def get_devices(enrollment_id: Optional[str] = None) -> List[Device]:
    params = {}
    if enrollment_id:
        params["enrolment_id"] = enrollment_id
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SVC_URL}/api/v1/devices/", params=params)
        response.raise_for_status()
        return [Device(**item) for item in response.json()]


async def get_device(device_id: UUID) -> Optional[Device]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SVC_URL}/api/v1/devices/{device_id}")
        if response.status_code == 200:
            return Device(**response.json())
        return None


async def update_device(device_id: UUID, device_in: DeviceUpdate) -> Optional[Device]:
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{USER_SVC_URL}/api/v1/devices/{device_id}",
            json=device_in.model_dump(mode='json', exclude_unset=True)
        )
        if response.status_code == 200:
            return Device(**response.json())
        return None


async def delete_device(device_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{USER_SVC_URL}/api/v1/devices/{device_id}")
        return response.status_code == 204
