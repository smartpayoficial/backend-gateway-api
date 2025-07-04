import os
from typing import List, Optional
from uuid import UUID

import httpx
from app.models.enrolment import EnrolmentCreate, EnrolmentDB

USER_SVC_URL = os.getenv("USER_SVC_URL", "http://localhost:8002")


async def get_enrolments() -> List[EnrolmentDB]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SVC_URL}/api/v1/enrolments/")
        response.raise_for_status()
        return [EnrolmentDB(**item) for item in response.json()]


async def get_enrolment(enrolment_id: UUID) -> Optional[EnrolmentDB]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SVC_URL}/api/v1/enrolments/{enrolment_id}")
        if response.status_code == 200:
            return EnrolmentDB(**response.json())
        return None


async def create_enrolment(enrolment_in: EnrolmentCreate) -> Optional[EnrolmentDB]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{USER_SVC_URL}/api/v1/enrolments/",
            json=enrolment_in.model_dump(mode='json')
        )
        if response.status_code == 201:
            return EnrolmentDB(**response.json())
        return None


async def delete_enrolment(enrolment_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{USER_SVC_URL}/api/v1/enrolments/{enrolment_id}")
        return response.status_code == 204
