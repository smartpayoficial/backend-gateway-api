from typing import List, Optional
from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, Query, Response, status

from app.models.configuration import (
    ConfigurationCreate,
    ConfigurationDB,
    ConfigurationUpdate,
)
from app.services import configuration as configuration_service

router = APIRouter(tags=["configurations"])


@router.post("/", response_model=ConfigurationDB, status_code=status.HTTP_201_CREATED)
async def create_configuration(config: ConfigurationCreate):
    """
    Create a new configuration
    """
    new_config = await configuration_service.create_configuration(config)
    if not new_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Configuration could not be created.",
        )
    return new_config


@router.get("/", response_model=List[ConfigurationDB])
async def get_configurations(
    key: Optional[str] = Query(
        None, description="Filter configurations by key (partial match)"
    )
):
    """
    Get all configurations
    Optionally filter by key (partial match)
    """
    try:
        return await configuration_service.get_configurations(key=key)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from downstream service: {e.response.text}",
        )


@router.get("/{configuration_id}", response_model=ConfigurationDB)
async def get_configuration(configuration_id: UUID):
    """
    Get a specific configuration by ID
    """
    config = await configuration_service.get_configuration(configuration_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config


@router.patch("/{configuration_id}", response_model=ConfigurationDB)
async def update_configuration(configuration_id: UUID, config: ConfigurationUpdate):
    """
    Update a configuration
    """
    updated = await configuration_service.update_configuration(configuration_id, config)
    if not updated:
        raise HTTPException(
            status_code=404, detail="Configuration not found or not updated"
        )
    return updated


@router.delete("/{configuration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_configuration(configuration_id: UUID):
    """
    Delete a configuration
    """
    deleted = await configuration_service.delete_configuration(configuration_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
