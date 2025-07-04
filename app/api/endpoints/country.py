from typing import List
from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, Path, status

from app.models.location import CountryCreate, CountryDB, CountryUpdate
from app.services import location as location_service

router = APIRouter()


@router.post("/", response_model=CountryDB, status_code=status.HTTP_201_CREATED)
async def create_country(country_in: CountryCreate):
    country = await location_service.create_country(country_in)
    if not country:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Country could not be created.",
        )
    return country


@router.get("/", response_model=List[CountryDB])
async def get_all_countries():
    try:
        return await location_service.get_countries()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from downstream service: {e.response.text}",
        )


@router.get("/{country_id}", response_model=CountryDB)
async def get_country_by_id(country_id: UUID = Path(...)):
    country = await location_service.get_country(country_id)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country


@router.patch("/{country_id}", response_model=CountryDB)
async def update_country(country_id: UUID, country_in: CountryUpdate):
    country = await location_service.update_country(country_id, country_in)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country


@router.delete("/{country_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_country(country_id: UUID):
    success = await location_service.delete_country(country_id)
    if not success:
        raise HTTPException(status_code=404, detail="Country not found")
