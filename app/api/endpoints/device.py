from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status

from app.models.device import DeviceCreate, DeviceDB, DeviceUpdate
from app.servicios import device as device_service

router = APIRouter()


@router.get("/", response_model=List[DeviceDB])
async def list_devices():
    """Lista todos los dispositivos."""
    return await device_service.get_devices()


@router.get("/{device_id}", response_model=DeviceDB)
async def get_device(device_id: UUID):
    """Obtiene un dispositivo por su ID."""
    dev = await device_service.get_device(device_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return dev


@router.post("/", response_model=DeviceDB, status_code=status.HTTP_201_CREATED)
async def create_device(device: DeviceCreate):
    """Crea un nuevo dispositivo."""
    return await device_service.create_device(device)


@router.patch("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_device(device_id: UUID, device: DeviceUpdate):
    """Actualiza un dispositivo existente."""
    await device_service.update_device(device_id, device)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(device_id: UUID):
    """Elimina un dispositivo por su ID."""
    ok = await device_service.delete_device(device_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
