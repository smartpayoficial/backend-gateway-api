from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, status

from app.models.location import RegionCreate, RegionDB, RegionUpdate
from app.servicios import location as location_service

router = APIRouter()


@router.post("/", response_model=RegionDB, status_code=status.HTTP_201_CREATED)
async def create_region(region_in: RegionCreate):
    return await location_service.create_region(region_in)


@router.get("/", response_model=List[RegionDB])
async def get_all_regions():
    return await location_service.get_regions()


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
