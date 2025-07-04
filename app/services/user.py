import os
from typing import List, Optional
from uuid import UUID

import httpx
from app.models.user import User, UserCreate, UserUpdate

USER_SVC_URL = os.getenv("USER_SVC_URL", "http://localhost:8002")
USER_API_URL = f"{USER_SVC_URL}/api/v1/users"


async def create_user(user_in: UserCreate) -> User:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{USER_API_URL}/", json=user_in.model_dump(mode="json"))
        response.raise_for_status()  # Will raise an exception for 4xx/5xx responses
        return User(**response.json())


async def get_user(user_id: UUID) -> Optional[User]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_API_URL}/{user_id}")
        if response.status_code == 200:
            return User(**response.json())
        return None


async def get_users(role_name: Optional[str] = None, state: Optional[str] = None) -> List[User]:
    params = {}
    if role_name:
        params["role_name"] = role_name
    if state:
        params["state"] = state

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_API_URL}/", params=params)
        response.raise_for_status()
        return [User(**item) for item in response.json()]


async def update_user(user_id: UUID, user_in: UserUpdate) -> Optional[User]:
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{USER_API_URL}/{user_id}",
            json=user_in.model_dump(mode="json", exclude_unset=True),
        )
        if response.status_code == 200:
            return User(**response.json())
        return None


async def delete_user(user_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{USER_API_URL}/{user_id}")
        return response.status_code == 204
