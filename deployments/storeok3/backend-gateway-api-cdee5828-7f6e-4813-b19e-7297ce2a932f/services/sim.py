import os
from typing import List, Optional
from uuid import UUID

import httpx
from app.models.sim import Sim, SimCreate, SimUpdate

USER_SVC_URL = os.getenv("USER_SVC_URL", "http://localhost:8002")
SIM_API_URL = f"{USER_SVC_URL}/api/v1/sims"


async def create_sim(sim_in: SimCreate) -> Optional[Sim]:
    async with httpx.AsyncClient() as client:
        response = await client.post(SIM_API_URL, json=sim_in.model_dump(mode="json"))
        if response.status_code == 201:
            return Sim(**response.json())
        return None


async def get_sims(skip: int, limit: int) -> List[Sim]:
    params = {"skip": skip, "limit": limit}
    async with httpx.AsyncClient() as client:
        response = await client.get(SIM_API_URL, params=params)
        response.raise_for_status()
        return [Sim(**item) for item in response.json()]


async def get_sims_by_device(device_id: UUID, skip: int, limit: int) -> List[Sim]:
    params = {"skip": skip, "limit": limit}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SIM_API_URL}/by-device/{device_id}", params=params)
        response.raise_for_status()
        return [Sim(**item) for item in response.json()]


async def get_sim_by_id(sim_id: UUID) -> Optional[Sim]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SIM_API_URL}/{sim_id}")
        if response.status_code == 200:
            return Sim(**response.json())
        return None


async def get_sim_by_number(number: str) -> Optional[Sim]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SIM_API_URL}/number/{number}")
        if response.status_code == 200:
            return Sim(**response.json())
        return None


async def update_sim(sim_id: UUID, sim_update: SimUpdate) -> Optional[Sim]:
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{SIM_API_URL}/{sim_id}",
            json=sim_update.model_dump(mode="json", exclude_unset=True),
        )
        if response.status_code == 200:
            return Sim(**response.json())
        return None


async def delete_sim(sim_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{SIM_API_URL}/{sim_id}")
        return response.status_code == 204
