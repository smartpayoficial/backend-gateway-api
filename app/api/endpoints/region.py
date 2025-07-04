from typing import List
from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, Path, status

from app.models.location import RegionCreate, RegionDB, RegionUpdate
from app.services import location as location_service

router = APIRouter()


@router.post("/", response_model=RegionDB, status_code=status.HTTP_201_CREATED)
async def create_region(region_in: RegionCreate):
    region = await location_service.create_region(region_in)
    if not region:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Region could not be created.",
        )
    return region


@router.get("/", response_model=List[RegionDB])
async def get_all_regions():
    try:
        return await location_service.get_regions()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from downstream service: {e.response.text}",
        )


@router.get("/{region_id}", response_model=RegionDB)
async def get_region_by_id(region_id: UUID = Path(...)):
    region = await location_service.get_region(region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return region


@router.patch("/{region_id}", response_model=RegionDB)
async def update_region(region_id: UUID, region_in: RegionUpdate):
    region = await location_service.update_region(region_id, region_in)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return region


@router.delete("/{region_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_region(region_id: UUID):
    success = await location_service.delete_region(region_id)
    if not success:
        raise HTTPException(status_code=404, detail="Region not found")
