import os
from typing import List, Optional
from uuid import UUID

import httpx

from app.models.role import RoleCreate, RoleDB, RoleUpdate

DB_SVC_URL = os.getenv("USER_SVC_URL") or os.getenv("DB_API", "http://localhost:8002")
ROLE_API_PREFIX = "/api/v1"
INTERNAL_HDR = {"X-Internal-Request": "true"}

# CRUD Functions for Role entity


async def get_role(role_id: UUID) -> Optional[RoleDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ROLE_API_PREFIX}/roles/{role_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        return RoleDB(**resp.json())
    return None


async def get_roles() -> List[RoleDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ROLE_API_PREFIX}/roles"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        return [RoleDB(**item) for item in resp.json()]
    return []


async def create_role(role: RoleCreate) -> RoleDB:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ROLE_API_PREFIX}/roles"
        resp = await client.post(
            url, headers=INTERNAL_HDR, json=role.model_dump(mode="json")
        )
    resp.raise_for_status()
    return RoleDB(**resp.json())


async def update_role(role_id: UUID, role: RoleUpdate) -> Optional[RoleDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ROLE_API_PREFIX}/roles/{role_id}"
        resp = await client.patch(
            url, headers=INTERNAL_HDR, json=role.dict(exclude_none=True)
        )
    if resp.status_code == 204:
        return None
    resp.raise_for_status()
    return RoleDB(**resp.json())


async def delete_role(role_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ROLE_API_PREFIX}/roles/{role_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)
    return resp.status_code == 204
