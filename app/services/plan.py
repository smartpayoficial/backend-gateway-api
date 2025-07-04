import os
from typing import List, Optional
from uuid import UUID

import httpx
from app.models.plan import Plan, PlanCreate, PlanDB, PlanRaw, PlanUpdate

USER_SVC_URL = os.getenv("USER_SVC_URL", "http://localhost:8002")
PLAN_API_URL = f"{USER_SVC_URL}/api/v1/plans"


async def create_plan(plan_in: PlanCreate) -> Optional[Plan]:
    async with httpx.AsyncClient() as client:
        response = await client.post(PLAN_API_URL, json=plan_in.model_dump(mode="json"))
        if response.status_code == 201:
            return Plan(**response.json())
        return None


async def get_all_plans() -> List[PlanRaw]:
    async with httpx.AsyncClient() as client:
        response = await client.get(PLAN_API_URL)
        response.raise_for_status()
        return [PlanRaw(**item) for item in response.json()]


async def get_plan_by_id(plan_id: UUID) -> Optional[PlanRaw]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PLAN_API_URL}/{plan_id}")
        if response.status_code == 200:
            return PlanRaw(**response.json())
        return None


async def update_plan(plan_id: UUID, plan_update: PlanUpdate) -> Optional[PlanDB]:
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{PLAN_API_URL}/{plan_id}",
            json=plan_update.model_dump(mode="json", exclude_unset=True),
        )
        if response.status_code == 200:
            return PlanDB(**response.json())
        return None


async def delete_plan(plan_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{PLAN_API_URL}/{plan_id}")
        return response.status_code == 204
