import os
from typing import Optional
from uuid import UUID

import httpx

from app.models.user import UserOut, UserUpdate

USER_SVC_URL = os.getenv("USER_SVC_URL") or os.getenv("DB_API", "http://localhost:8002")
USER_API_PREFIX = "/api/v1"
INTERNAL_HDR = {"X-Internal-Request": "true"}


async def update_user(user_id: UUID, user: UserUpdate) -> Optional[UserOut]:
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{USER_API_PREFIX}/users/{user_id}"
        resp = await client.patch(
            url, headers=INTERNAL_HDR, json=user.dict(exclude_none=True)
        )
    if resp.status_code == 204:
        return None
    resp.raise_for_status()
    return UserOut(**resp.json())


async def delete_user(user_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{USER_API_PREFIX}/users/{user_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)
    return resp.status_code == 204
