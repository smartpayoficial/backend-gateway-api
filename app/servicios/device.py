import os
from typing import List, Optional
from uuid import UUID

import httpx
from fastapi import HTTPException
from httpx import HTTPStatusError

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
    try:
        async with httpx.AsyncClient() as client:
            url = f"{USER_SVC_URL}{DEVICE_API_PREFIX}/devices/"
            resp = await client.post(
                url,
                headers=INTERNAL_HDR,
                content=device_in.model_dump_json(exclude_unset=True),
            )
            resp.raise_for_status()
        return DeviceDB(**resp.json())
    except HTTPStatusError as e:
        if e.response.status_code == 409:
            try:
                detail = e.response.json().get("detail", e.response.text)
            except Exception:
                detail = e.response.text
            raise HTTPException(
                status_code=409, detail=f"Device already exists: {detail}"
            )
        elif e.response.status_code == 400:
            try:
                detail = e.response.json().get("detail", e.response.text)
            except Exception:
                detail = e.response.text
            raise HTTPException(
                status_code=400, detail=f"Invalid data provided: {detail}"
            )
        raise e


async def update_device(device_id: UUID, device_in: DeviceUpdate) -> Optional[DeviceDB]:
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{DEVICE_API_PREFIX}/devices/{device_id}"
        resp = await client.patch(
            url,
            headers=INTERNAL_HDR,
            content=device_in.model_dump_json(exclude_unset=True),
        )

    if resp.status_code == 200:
        return DeviceDB(**resp.json())
    if resp.status_code == 204:
        return await get_device(device_id)

    return None

    # TODO: Logging for UPDATE needs a valid ActionType in the enum.
    # action_log = ActionCreate(
    #     device_id=device_id,
    #     applied_by_id=applied_by_id,
    #     action="UPDATE",
    #     description=f"Device {device_id} updated.",
    # )
    # await action_service.create_action(action_log)


async def delete_device(device_id: UUID) -> bool:
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
