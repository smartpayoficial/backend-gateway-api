import os
from typing import List, Optional
from uuid import UUID

import httpx
from app.models.factory_reset_protection import (
    FactoryResetProtectionCreate,
    FactoryResetProtectionResponse,
    FactoryResetProtectionState,
    FactoryResetProtectionUpdate,
)

USER_SVC_URL = os.getenv("USER_SVC_URL", "http://localhost:8002")
FRP_API_URL = f"{USER_SVC_URL}/api/v1/factory-reset-protections"


async def create_factory_reset_protection(
    frp_in: FactoryResetProtectionCreate,
) -> Optional[FactoryResetProtectionResponse]:
    async with httpx.AsyncClient() as client:
        response = await client.post(FRP_API_URL, json=frp_in.model_dump(mode="json"))
        if response.status_code == 201:
            return FactoryResetProtectionResponse(**response.json())
        return None


async def get_factory_reset_protections(
    state: Optional[FactoryResetProtectionState] = None,
) -> List[FactoryResetProtectionResponse]:
    params = {}
    if state:
        params["state"] = state.value
    async with httpx.AsyncClient() as client:
        response = await client.get(FRP_API_URL, params=params)
        response.raise_for_status()
        return [FactoryResetProtectionResponse(**item) for item in response.json()]

async def get_factory_reset_protection_by_account(
    account_id: str
)  -> Optional[FactoryResetProtectionResponse]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FRP_API_URL}/accountId/{account_id}")
        if response.status_code == 200:
            return FactoryResetProtectionResponse(**response.json())
        return None


async def get_factory_reset_protection(
    frp_id: UUID,
) -> Optional[FactoryResetProtectionResponse]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FRP_API_URL}/{frp_id}")
        if response.status_code == 200:
            return FactoryResetProtectionResponse(**response.json())
        return None


async def update_factory_reset_protection(
    frp_id: UUID, frp_update: FactoryResetProtectionUpdate
) -> Optional[FactoryResetProtectionResponse]:
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{FRP_API_URL}/{frp_id}",
            json=frp_update.model_dump(mode="json", exclude_unset=True),
        )
        if response.status_code == 200:
            return FactoryResetProtectionResponse(**response.json())
        return None


async def delete_factory_reset_protection(frp_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{FRP_API_URL}/{frp_id}")
        return response.status_code == 204
