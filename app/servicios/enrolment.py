import os
from typing import List, Optional
from uuid import UUID

import httpx

from app.models.enrolment import EnrolmentCreate, EnrolmentDB, EnrolmentUpdate

DB_SVC_URL = os.getenv("USER_SVC_URL") or os.getenv("DB_API", "http://localhost:8002")
ENROLMENT_API_PREFIX = "/api/v1"
INTERNAL_HDR = {"X-Internal-Request": "true"}

# CRUD Functions for Enrolment entity


async def get_enrolment(enrolment_id: UUID) -> Optional[EnrolmentDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ENROLMENT_API_PREFIX}/enrolments/{enrolment_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        return EnrolmentDB(**resp.json())
    return None


async def get_enrolments() -> List[EnrolmentDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ENROLMENT_API_PREFIX}/enrolments"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        return [EnrolmentDB(**item) for item in resp.json()]
    return []


async def create_enrolment(enrolment: EnrolmentCreate) -> EnrolmentDB:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ENROLMENT_API_PREFIX}/enrolments"
        resp = await client.post(
            url, headers=INTERNAL_HDR, json=enrolment.model_dump(mode="json")
        )
    resp.raise_for_status()
    return EnrolmentDB(**resp.json())


async def update_enrolment(
    enrolment_id: UUID, enrolment: EnrolmentUpdate
) -> Optional[EnrolmentDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ENROLMENT_API_PREFIX}/enrolments/{enrolment_id}"
        resp = await client.patch(
            url, headers=INTERNAL_HDR, json=enrolment.dict(exclude_none=True)
        )
    if resp.status_code == 204:
        return None
    resp.raise_for_status()
    return EnrolmentDB(**resp.json())


async def delete_enrolment(enrolment_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ENROLMENT_API_PREFIX}/enrolments/{enrolment_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)
    return resp.status_code == 204
