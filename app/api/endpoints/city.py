from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, Response, status

from app.models.location import CityCreate, CityDB, CityUpdate
from app.servicios import location as location_service

router = APIRouter()


@router.post("/", response_model=CityDB, status_code=status.HTTP_201_CREATED)
async def create_city(city_in: CityCreate):
    return await location_service.create_city(city_in)


@router.get("/", response_model=List[CityDB])
async def get_all_cities():
    return await location_service.get_cities()


@router.get("/{city_id}", response_model=CityDB)
async def get_city_by_id(city_id: UUID = Path(...)):
    city = await location_service.get_city(city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city


@router.patch("/{city_id}", response_model=CityDB)
async def update_city(city_id: UUID, city_in: CityUpdate):
    city = await location_service.update_city(city_id, city_in)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city


@router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_city(city_id: UUID):
    success = await location_service.delete_city(city_id)
    if not success:
        raise HTTPException(status_code=404, detail="City not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
