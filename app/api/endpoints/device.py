from typing import Dict, List, Optional
from uuid import UUID

import httpx
import os
from fastapi import APIRouter, HTTPException, Path, Query, status

# Imports for Device
from app.models.device import Device, DeviceCreate, DeviceUpdate

# Imports for Location
from app.models.location import LocationCreate, LocationDB
from app.services import device as device_service
from app.services import location as location_service


router = APIRouter()


# --- Device Endpoints ---


@router.post("/", response_model=Device, status_code=status.HTTP_201_CREATED)
async def create_device(device_in: DeviceCreate):
    device = await device_service.create_device(device_in)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device could not be created.",
        )
    return device


@router.get("/", response_model=List[Device])
async def get_all_devices(
    enrollment_id: Optional[str] = Query(None), user_id: Optional[UUID] = Query(None)
):
    try:
        return await device_service.get_devices(
            enrollment_id=enrollment_id, user_id=user_id
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from downstream service: {e.response.text}",
        )


@router.get("/count", response_model=Dict[str, int])
async def get_device_count():
    try:
        count = await device_service.get_device_count()
        return {"count": count}
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from downstream service: {e.response.text}",
        )


@router.get("/{device_id}", response_model=Device)
async def get_device_by_id(device_id: UUID = Path(...)):
    device = await device_service.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.patch("/{device_id}", response_model=Device)
async def update_device(device_id: UUID, device_in: DeviceUpdate):
    device = await device_service.update_device(device_id, device_in)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(device_id: UUID):
    success = await device_service.delete_device(device_id)
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")


# --- Location Endpoints (related to Devices) ---


@router.post(
    "/locations/", response_model=LocationDB, status_code=status.HTTP_201_CREATED
)
async def create_location(location_in: LocationCreate):
    # Check if device exists
    async with httpx.AsyncClient() as client:
        try:
            db_api = os.getenv("DB_API", "http://smartpay-db-api:8002")
            response = await client.get(
                f"{db_api}/api/v1/devices/{location_in.device_id}"
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Device with ID {location_in.device_id} not found",
                )
            else:
                # If we get an error other than 404, we return the same status and detail
                detail = e.response.json().get("detail", "Error from device service")
                raise HTTPException(status_code=e.response.status_code, detail=detail)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")

    location = await location_service.create_location(location_in)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location could not be created.",
        )
    return location


@router.get("/locations/", response_model=List[LocationDB])
async def get_all_locations(device_id: Optional[UUID] = Query(None)):
    try:
        return await location_service.get_locations(device_id=device_id)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from downstream service: {e.response.text}",
        )


@router.get("/locations/{location_id}", response_model=LocationDB)
async def get_location_by_id(location_id: UUID = Path(...)):
    location = await location_service.get_location(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(location_id: UUID):
    success = await location_service.delete_location(location_id)
    if not success:
        raise HTTPException(status_code=404, detail="Location not found")
