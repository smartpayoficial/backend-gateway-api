import os
from typing import List, Optional
from uuid import UUID

import httpx

from app.models.action import ActionCreate, ActionResponse, ActionState, ActionUpdate

# The DB service is the same one used for users and payments.
DB_SVC_URL = os.getenv("DB_API", "http://localhost:8002")
ACTION_API_PREFIX = "/api/v1/actions"
INTERNAL_HDR = {"X-Internal-Request": "true"}


async def create_action(action: ActionCreate) -> ActionResponse:
    """
    Sends a request to the DB microservice to create a new action.
    """
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ACTION_API_PREFIX}"
        resp = await client.post(
            url, headers=INTERNAL_HDR, json=action.model_dump(mode="json")
        )
    resp.raise_for_status()
    return ActionResponse(**resp.json())


async def get_action(action_id: UUID) -> Optional[ActionResponse]:
    """
    Retrieves a single action by its ID from the DB microservice.
    """
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ACTION_API_PREFIX}/{action_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        return ActionResponse(**resp.json())
    return None


async def get_actions(
    device_id: Optional[UUID] = None, state: Optional[ActionState] = None
) -> List[ActionResponse]:
    """
    Retrieves a list of actions, optionally filtered by device_id and state.
    """
    params = {}
    if device_id:
        params["device_id"] = str(device_id)
    if state:
        params["state"] = state.value

    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ACTION_API_PREFIX}"
        resp = await client.get(url, headers=INTERNAL_HDR, params=params or None)

    if resp.status_code == 200:
        return [ActionResponse(**item) for item in resp.json()]
    return []


async def update_action(
    action_id: UUID, action_update: ActionUpdate
) -> Optional[ActionResponse]:
    """
    Updates an action in the DB microservice.
    """
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ACTION_API_PREFIX}/{action_id}"
        resp = await client.patch(
            url,
            headers=INTERNAL_HDR,
            json=action_update.model_dump(mode="json", exclude_unset=True),
        )
    if resp.status_code == 200:
        return ActionResponse(**resp.json())
    return None


async def delete_action(action_id: UUID) -> bool:
    """
    Deletes an action from the DB microservice.
    """
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ACTION_API_PREFIX}/{action_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)
    return resp.status_code == 200
