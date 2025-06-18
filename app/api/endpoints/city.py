from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status

from app.models.city import CityCreate, CityDB, CityUpdate
from app.servicios import city as city_service

router = APIRouter()


@router.get("/", response_model=List[CityDB])
async def list_cities():
    """Lista todas las ciudades."""
    return await city_service.get_cities()


@router.get("/{city_id}", response_model=CityDB)
async def get_city(city_id: UUID):
    """Obtiene una ciudad por su ID."""
    city = await city_service.get_city(city_id)
    if not city:
        raise HTTPException(status_code=404, detail="Ciudad no encontrada")
    return city


@router.post("/", response_model=CityDB, status_code=status.HTTP_201_CREATED)
async def create_city(city: CityCreate):
    """Crea una nueva ciudad."""
    return await city_service.create_city(city)


@router.patch("/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_city(city_id: UUID, city: CityUpdate):
    """Actualiza una ciudad existente."""
    await city_service.update_city(city_id, city)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_city(city_id: UUID):
    """Elimina una ciudad por su ID."""
    ok = await city_service.delete_city(city_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Ciudad no encontrada")
