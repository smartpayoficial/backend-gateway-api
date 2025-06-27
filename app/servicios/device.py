import os
from typing import List, Optional
from uuid import UUID

import httpx

from app.models.action import ActionCreate
from app.models.device import DeviceCreate, DeviceDB, DeviceUpdate
from app.servicios import action as action_service

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


async def create_device(device_in: DeviceCreate) -> DeviceDB:
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{DEVICE_API_PREFIX}/devices"
        resp = await client.post(
            url, headers=INTERNAL_HDR, json=device_in.model_dump(mode="json")
        )
    resp.raise_for_status()
    new_device = DeviceDB(**resp.json())

    # Log the action
    action_log = ActionCreate(
        action_type="CREATE",
        details=f"Device created with serial {new_device.serial_number}",
        device_id=new_device.id,
    )
    await action_service.create_action(action_log)

    return new_device


async def update_device(device_id: UUID, device_in: DeviceUpdate) -> Optional[DeviceDB]:
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{DEVICE_API_PREFIX}/devices/{device_id}"
        resp = await client.patch(
            url, headers=INTERNAL_HDR, json=device_in.dict(exclude_none=True)
        )
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    updated_device = DeviceDB(**resp.json())

    # Log the action
    action_log = ActionCreate(
        action_type="UPDATE",
        details=f"Device {device_id} updated.",
        device_id=device_id,
    )
    await action_service.create_action(action_log)

    return updated_device


async def delete_device(device_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{DEVICE_API_PREFIX}/devices/{device_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)

    if resp.status_code == 204:
        # Log the action
        action_log = ActionCreate(
            action_type="DELETE",
            details=f"Device {device_id} deleted.",
            device_id=device_id,
        )
        await action_service.create_action(action_log)
        return True

    return False
