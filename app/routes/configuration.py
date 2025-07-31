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


@router.post("/create-default-configs/", response_model=List[ConfigurationDB], status_code=status.HTTP_201_CREATED)
async def create_default_configurations(store_id: UUID):
    """
    Create default configurations for a store
    
    This endpoint creates a set of predefined configurations with the specified store_id:
    - blocked_message: Message displayed when device is blocked due to non-payment
    - blocked_sim: Message displayed when SIM card is not active
    - payment_message: Message displayed when payment is completed
    - payment_reminder: Message displayed as a payment reminder
    
    Returns the created configurations
    """
    default_configs = [
        ConfigurationCreate(
            key="blocked_message",
            value="Mensaje de Bloqueo",
            description="Tu dispositivo ha sido bloqueado por no pago para seguirlo usando realiza el pago.",
            store_id=store_id
        ),
        ConfigurationCreate(
            key="blocked_sim",
            value="Mensaje de Bloqueo Sim",
            description="Esta Sim Card no esta activa por favor solicite la activación.",
            store_id=store_id
        ),
        ConfigurationCreate(
            key="payment_message",
            value="Mensaje de Pago",
            description="Has completado el pago total de tu dispositivo.\nLa aplicación SmartPay te solicitará desinstalará la desinstalación.",
            store_id=store_id
        ),
        ConfigurationCreate(
            key="payment_reminder",
            value="Recordatorio de Pago",
            description="Te recordamos que faltan %DAY% para la fecha de vencimiento de tu pago. ¡Gracias por tu atención!",
            store_id=store_id
        )
    ]
    
    created_configs = []
    for config in default_configs:
        new_config = await configuration_service.create_configuration(config)
        if not new_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Configuration '{config.key}' could not be created.",
            )
        created_configs.append(new_config)
    
    return created_configs


@router.post("/", response_model=ConfigurationDB, status_code=status.HTTP_201_CREATED)
async def create_configuration(
    config: ConfigurationCreate,
    store_id: Optional[UUID] = Query(None, description="Store ID to associate with this configuration")
):
    """
    Create a new configuration
    
    The configuration can be associated with a store either by:
    - Providing store_id as a query parameter
    - Including store_id in the request body
    
    If both are provided, the query parameter takes precedence
    """
    # If store_id is provided as a query parameter, it takes precedence over the one in the request body
    if store_id:
        config.store_id = store_id
    
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
    ),
    store_id: Optional[UUID] = Query(
        None, description="Filter configurations by store ID"
    )
):
    """
    Get all configurations
    Optionally filter by key (partial match) and/or store_id
    """
    try:
        return await configuration_service.get_configurations(key=key, store_id=store_id)
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
