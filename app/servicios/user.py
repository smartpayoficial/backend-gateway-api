import logging
import os
from typing import List, Optional
from uuid import UUID

import httpx

from app.models.user import User, UserCreate, UserUpdate
from app.servicios.city import get_city

USER_SVC_URL = os.getenv("USER_SVC_URL") or os.getenv("DB_API", "http://localhost:8002")
USER_API_PREFIX = "/api/v1"
INTERNAL_HDR = {"X-Internal-Request": "true"}


async def get_user(user_id: UUID) -> Optional[User]:
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{USER_API_PREFIX}/users/{user_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        user_data = resp.json()
        if user_data.get("city_id"):
            city_obj = await get_city(user_data["city_id"])
            user_data["city"] = city_obj.model_dump() if city_obj else None
        return User(**user_data)
    return None


async def get_users(
    role_name: Optional[str] = None, state: Optional[str] = None
) -> List[User]:
    params = {}
    if role_name:
        params["role_name"] = role_name
    if state:
        params["state"] = state
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{USER_API_PREFIX}/users/"
        resp = await client.get(url, params=params, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        users_data = resp.json()
        enriched_users = []
        for user_data in users_data:
            if user_data.get("city_id"):
                city_obj = await get_city(user_data["city_id"])
                user_data["city"] = city_obj.model_dump() if city_obj else None
            enriched_users.append(User(**user_data))
        return enriched_users
    return []


async def create_user(user_in: UserCreate) -> User:
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{USER_API_PREFIX}/users"
        resp = await client.post(
            url, headers=INTERNAL_HDR, json=user_in.model_dump(mode="json")
        )

    if resp.is_client_error or resp.is_server_error:
        logging.error(f"User service returned an error: {resp.status_code} {resp.text}")
    resp.raise_for_status()

    response_data = resp.json()
    new_user_id = response_data.get("user_id")
    if not new_user_id:
        raise Exception("User service did not return a user_id after creation.")

    created_user = await get_user(new_user_id)
    if not created_user:
        raise Exception(f"Could not retrieve user {new_user_id} after creation.")

    return created_user


async def update_user(user_id: UUID, user: UserUpdate) -> Optional[User]:
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{USER_API_PREFIX}/users/{user_id}"
        resp = await client.patch(
            url, headers=INTERNAL_HDR, json=user.model_dump(exclude_none=True)
        )
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return User(**resp.json())


async def delete_user(user_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{USER_API_PREFIX}/users/{user_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)
    if resp.status_code == 404:
        return False
    return resp.status_code == 204
