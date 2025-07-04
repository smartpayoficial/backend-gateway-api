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
        # Convert the model to a dictionary and explicitly include all fields
        update_data = plan_update.model_dump(mode="json", exclude_unset=False)

        # Log the data being sent (for debugging)
        print(f"Sending update data to plan service: {update_data}")

        response = await client.patch(
            f"{PLAN_API_URL}/{plan_id}",
            json=update_data,
        )

        # Handle different status codes
        if response.status_code == 200:
            # Directly use the response data with the updated PlanDB model
            return PlanDB(**response.json())
        elif response.status_code == 204:
            # If the backend returns 204 No Content, try to get the updated plan
            updated_plan = await get_plan_by_id(plan_id)
            if updated_plan:
                # Convert to dict and use with PlanDB
                return PlanDB(**updated_plan.model_dump())

        return None


async def delete_plan(plan_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{PLAN_API_URL}/{plan_id}")
        return response.status_code == 204
