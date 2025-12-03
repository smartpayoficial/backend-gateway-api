import os
from typing import List, Optional
from uuid import UUID

import httpx

from app.models.television import Television, TelevisionCreate, TelevisionUpdate

USER_SVC_URL = os.getenv("USER_SVC_URL", "http://localhost:8002")


async def create_television(television_in: TelevisionCreate) -> Optional[Television]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{USER_SVC_URL}/api/v1/televisions/", json=television_in.model_dump(mode="json")
        )
        if response.status_code == 201:
            return Television(**response.json())
        return None


async def get_televisions(
    enrollment_id: Optional[str] = None, user_id: Optional[UUID] = None
) -> List[Television]:
    params = {}
    if enrollment_id:
        params["enrolment_id"] = enrollment_id
    if user_id:
        params["user_id"] = str(user_id)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SVC_URL}/api/v1/televisions/", params=params)
        response.raise_for_status()
        return [Television(**item) for item in response.json()]


async def get_television(television_id: UUID) -> Optional[Television]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SVC_URL}/api/v1/televisions/{television_id}")
        if response.status_code == 200:
            return Television(**response.json())
        return None


async def update_television(television_id: UUID, television_in: TelevisionUpdate) -> Optional[Television]:
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{USER_SVC_URL}/api/v1/televisions/{television_id}",
            json=television_in.model_dump(mode="json", exclude_unset=True),
        )
        if response.status_code == 200:
            return Television(**response.json())
        return None


async def delete_television(television_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{USER_SVC_URL}/api/v1/televisions/{television_id}")
        return response.status_code == 204


async def get_television_count() -> int:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SVC_URL}/api/v1/televisions/count")
        response.raise_for_status()
        return response.json().get("count", 0)
