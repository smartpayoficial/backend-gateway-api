import os
from typing import List, Optional
from uuid import UUID

import httpx

from app.models.role import Role, RoleCreate, RoleUpdate

USER_SVC_URL = os.getenv("USER_SVC_URL", "http://localhost:8002")
ROLE_API_URL = f"{USER_SVC_URL}/api/v1/roles/"


async def get_roles(name: Optional[str] = None) -> List[Role]:
    params = {}
    if name:
        params["name"] = name
    async with httpx.AsyncClient() as client:
        response = await client.get(ROLE_API_URL, params=params)
        response.raise_for_status()
        return [Role(**item) for item in response.json()]


async def get_role(role_id: UUID) -> Optional[Role]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ROLE_API_URL}{role_id}")
        if response.status_code == 200:
            return Role(**response.json())
        return None


async def create_role(role_in: RoleCreate) -> Optional[Role]:
    async with httpx.AsyncClient() as client:
        response = await client.post(ROLE_API_URL, json=role_in.model_dump(mode="json"))
        if response.status_code == 201:
            return Role(**response.json())
        return None


async def update_role(role_id: UUID, role_update: RoleUpdate) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{ROLE_API_URL}{role_id}",
            json=role_update.model_dump(mode="json", exclude_unset=True),
        )
        return response.status_code == 204


async def delete_role(role_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{ROLE_API_URL}{role_id}")
        return response.status_code == 204
