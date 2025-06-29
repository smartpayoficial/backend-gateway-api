import os
from typing import List, Optional
from uuid import UUID

import httpx

from app.models.factory_reset_protection import FactoryResetProtectionResponse, FactoryResetProtectionCreate, FactoryResetProtectionState, FactoryResetProtectionUpdate

# The DB service is the same one used for users and payments.
DB_SVC_URL = os.getenv("DB_API", "http://localhost:8002")
ACTION_API_PREFIX = "/api/v1/factoryResetProtection"
INTERNAL_HDR = {"X-Internal-Request": "true"}


async def create_factory_reset_protection(factory: FactoryResetProtectionCreate) -> FactoryResetProtectionResponse:
    """
    Sends a request to the DB microservice to create a new action.
    """
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ACTION_API_PREFIX}"
        resp = await client.post(
            url, headers=INTERNAL_HDR, json=factory.model_dump(mode="json")
        )
    resp.raise_for_status()
    return FactoryResetProtectionResponse(**resp.json())


async def get_factory_reset_protection(factory_id: UUID) -> Optional[FactoryResetProtectionResponse]:
    """
    Retrieves a single action by its ID from the DB microservice.
    """
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ACTION_API_PREFIX}/{factory_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        return FactoryResetProtectionResponse(**resp.json())
    return None

async def get_factory_reset_protection_by_account(account_id: str) -> Optional[FactoryResetProtectionResponse]:
    """
    Retrieves a single action by its ID from the DB microservice.
    """
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ACTION_API_PREFIX}/accountId/{account_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        return FactoryResetProtectionResponse(**resp.json())
    return None


async def get_factory_reset_protections(
    state: Optional[FactoryResetProtectionState] = None
) -> List[FactoryResetProtectionResponse]:
    """
    Retrieves a list of actions, optionally filtered by device_id and state.
    """
    params = {}
    if state:
        params["state"] = state.value

    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ACTION_API_PREFIX}"
        resp = await client.get(url, headers=INTERNAL_HDR, params=params or None)

    if resp.status_code == 200:
        return [FactoryResetProtectionResponse(**item) for item in resp.json()]
    return []


async def update_factory_reset_protection(
    factory_id: UUID, factory_update: FactoryResetProtectionUpdate
) -> Optional[FactoryResetProtectionResponse]:
    """
    Updates an action in the DB microservice.
    """
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ACTION_API_PREFIX}/{factory_id}"
        resp = await client.patch(
            url,
            headers=INTERNAL_HDR,
            json=factory_update.model_dump(mode="json", exclude_unset=True),
        )
    if resp.status_code == 200:
        return FactoryResetProtectionResponse(**resp.json())
    return None


async def delete_factory_protection(factory_id: UUID) -> bool:
    """
    Deletes an action from the DB microservice.
    """
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ACTION_API_PREFIX}/{factory_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)
    return resp.status_code == 200
