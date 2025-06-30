from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.models.sim import Sim, SimCreate, SimUpdate
from app.servicios import sim as sim_service

router = APIRouter(tags=["sims"])

@router.post("/", response_model=Sim)
async def create_sim(sim: SimCreate):  
    return await sim_service.create_sim(sim)

@router.get("/", response_model=List[Sim])
async def get_all_sims(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return")
):
    return await sim_service.get_sims(skip = skip, limit = limit)

@router.get("/by-device/{device_id}", response_model=List[Sim])
async def get_sims_by_device(
    device_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return")
):
    return await sim_service.get_sims_by_device(device_id = device_id, skip = skip, limit = limit)

@router.get("/{sim_id}", response_model=Sim)
async def get_sim_by_id(sim_id: UUID):
    sim = await sim_service.get_sim_by_id(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Sim not found")
    return sim

@router.get("/number/{number}", response_model=Sim)
async def get_sim_by_id(number: str):
    sim = await sim_service.get_sim_by_number(number)
    if not sim:
        raise HTTPException(status_code=404, detail="Sim not found by number")
    return sim

@router.patch("/{sim_id}", response_model=Sim)
async def update_sim(sim_id: UUID, sim: SimUpdate):
    updated = await sim_service.update_sim(sim_id, sim)
    if not updated:
        raise HTTPException(status_code=404, detail="Sim not found or not updated")
    return updated

@router.delete("/{sim_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(sim_id: UUID):
    deleted = await sim_service.delet_sim(sim_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sim not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)