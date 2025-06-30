import os
from typing import List, Optional
from uuid import UUID

import httpx
from fastapi import HTTPException

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


async def get_devices(enrollment_id: Optional[str] = None) -> List[DeviceDB]:
    params = {}
    if enrollment_id:
        params["enrollment_id"] = enrollment_id

    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{DEVICE_API_PREFIX}/devices/"
        resp = await client.get(url, headers=INTERNAL_HDR, params=params or None)
    if resp.status_code == 200:
        return [DeviceDB(**item) for item in resp.json()]
    return []


async def create_device(device_in: DeviceCreate) -> DeviceDB:
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{DEVICE_API_PREFIX}/devices/"
        resp = await client.post(
            url, headers=INTERNAL_HDR, json=device_in.model_dump(mode="json")
        )

    if resp.status_code == 400:
        raise HTTPException(
            status_code=400, detail="enrollment id must be unique per device"
        )

    resp.raise_for_status()
    new_device = DeviceDB(**resp.json())

    # TODO: Resolve how to log this action. The ActionCreate model requires an
    # 'applied_by_id', but device creation may not have a user context.

    return new_device


async def update_device(
    device_id: UUID, device_in: DeviceUpdate, applied_by_id: UUID
) -> Optional[DeviceDB]:
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{DEVICE_API_PREFIX}/devices/{device_id}"
        resp = await client.patch(
            url, headers=INTERNAL_HDR, json=device_in.model_dump(exclude_none=True)
        )
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    updated_device = DeviceDB(**resp.json())

    # TODO: Logging for UPDATE needs a valid ActionType in the enum.
    # action_log = ActionCreate(
    #     device_id=device_id,
    #     applied_by_id=applied_by_id,
    #     action="UPDATE",
    #     description=f"Device {device_id} updated.",
    # )
    # await action_service.create_action(action_log)

    return updated_device


async def delete_device(device_id: UUID, applied_by_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{DEVICE_API_PREFIX}/devices/{device_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)

    if resp.status_code == 204:
        # TODO: Logging for DELETE needs a valid ActionType in the enum.
        # action_log = ActionCreate(
        #     device_id=device_id,
        #     applied_by_id=applied_by_id,
        #     action="DELETE",
        #     description=f"Device {device_id} deleted.",
        # )
        # await action_service.create_action(action_log)
        return True

    return False
