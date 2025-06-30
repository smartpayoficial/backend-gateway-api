import os
from typing import List, Optional
from uuid import UUID

import httpx

from app.models.sim import Sim, SimCreate, SimUpdate

# The DB service is the same one used for users and payments.
DB_SVC_URL = os.getenv("DB_API", "http://localhost:8002")
ACTION_API_PREFIX = "/api/v1/sims"
INTERNAL_HDR = {"X-Internal-Request": "true"}


async def create_sim(sim: SimCreate) -> Sim:
    """
    Sends a request to the DB microservice to create a new action.
    """
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ACTION_API_PREFIX}"
        resp = await client.post(
            url, headers=INTERNAL_HDR, json=sim.model_dump(mode="json")
        )
    resp.raise_for_status()
    return Sim(**resp.json())


async def get_sims(skip: int = 0, limit: int = 100) -> List[Sim]:
    """
    Retrieves a single action by its ID from the DB microservice.
    """
    params = {}

    if skip:
        params["skip"] = skip
    if limit:
        params["limit"] = limit
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ACTION_API_PREFIX}"
        resp = await client.get(url, params=params, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        return [Sim(**item) for item in resp.json()]
    return []

async def get_sims_by_device(device_id: UUID, skip: int = 0, limit: int = 100) -> List[Sim]:
    """
    Retrieves a single action by its ID from the DB microservice.
    """
    params = {}

    if skip:
        params["skip"] = skip
    if limit:
        params["limit"] = limit
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ACTION_API_PREFIX}/by-device/{device_id}" 
        resp = await client.get(url, params=params, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        return [Sim(**item) for item in resp.json()]
    return []

async def get_sim_by_id(sim_id: UUID) -> Optional[Sim]:
    """
    Retrieves a single action by its ID from the DB microservice.
    """
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ACTION_API_PREFIX}/{sim_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        return Sim(**resp.json())
    return None

async def get_sim_by_number(number: str) -> Optional[Sim]:
    """
    Retrieves a single action by its ID from the DB microservice.
    """
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ACTION_API_PREFIX}/number/{number}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        return Sim(**resp.json())
    return None

async def update_sim(
    sim_id: UUID, sim: SimUpdate
) -> Optional[Sim]:
    
    """
    Updates an action in the DB microservice.
    """
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ACTION_API_PREFIX}/{sim_id}"
        resp = await client.patch(
            url,
            headers=INTERNAL_HDR,
            json=sim.model_dump(mode="json", exclude_unset=True),
        )
    if resp.status_code == 200:
        return Sim(**resp.json())
    return None


async def delet_sim(sim_id: UUID) -> bool:
    """
    Deletes an action from the DB microservice.
    """

    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ACTION_API_PREFIX}/{sim_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)
    return resp.status_code == 200