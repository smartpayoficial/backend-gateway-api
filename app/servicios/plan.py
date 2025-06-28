import os
from typing import List, Optional
from uuid import UUID

import httpx
from fastapi.encoders import jsonable_encoder

from app.models.plan import PlanCreate, PlanUpdate

DB_SVC_URL = os.getenv("PLAN_SVC_URL") or os.getenv("DB_API", "http://localhost:8002")
PLAN_API_PREFIX = "/api/v1/plans"
INTERNAL_HDR = {"X-Internal-Request": "true"}


async def get_all_plans() -> List[dict]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{PLAN_API_PREFIX}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    resp.raise_for_status()
    return resp.json()


async def get_plan_by_id(plan_id: UUID) -> Optional[dict]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{PLAN_API_PREFIX}/{plan_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


async def create_plan(plan: PlanCreate) -> dict:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{PLAN_API_PREFIX}"

        json_compatible_plan_data = jsonable_encoder(plan)

        resp = await client.post(
            url, headers=INTERNAL_HDR, json=json_compatible_plan_data
        )

    resp.raise_for_status()
    print(f"DEBUG: Raw response from DB service for plan: {resp.json()}")
    return resp.json()


async def update_plan(plan_id: UUID, plan_update: PlanUpdate) -> Optional[dict]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{PLAN_API_PREFIX}/{plan_id}"
        resp = await client.patch(
            url, headers=INTERNAL_HDR, json=plan_update.dict(exclude_none=True)
        )
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    data = resp.json()
    return data


async def delete_plan(plan_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{PLAN_API_PREFIX}/{plan_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)
    return resp.status_code == 204
