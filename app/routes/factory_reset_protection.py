from typing import List, Optional
from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, Query, Response, status

from app.models.factory_reset_protection import (
    FactoryResetProtectionCreate,
    FactoryResetProtectionResponse,
    FactoryResetProtectionState,
    FactoryResetProtectionUpdate,
)
from app.services import factory_reset_protection as factory_reset_protection_service

router = APIRouter(tags=["factoryResetProtection"])


@router.post("/", response_model=FactoryResetProtectionResponse)
async def create_factory_reset_protection(
    frp_in: FactoryResetProtectionCreate,
    store_id: Optional[UUID] = Query(None, description="Store ID to associate with this protection")):
    """
    Create a new factory reset protection
    
    The protection can be associated with a store either by:
    - Providing store_id as a query parameter
    - Including store_id in the request body
    
    If both are provided, the query parameter takes precedence
    """
    # If store_id is provided as a query parameter, it takes precedence over the one in the request body
    if store_id:
        frp_in.store_id = store_id
        
    new_frp = await factory_reset_protection_service.create_factory_reset_protection(
        frp_in
    )
    if not new_frp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Factory reset protection could not be created.",
        )
    return new_frp


@router.get("/", response_model=List[FactoryResetProtectionResponse])
async def get_factory_reset_protections(
    state: Optional[FactoryResetProtectionState] = Query(None),
    store_id: Optional[UUID] = Query(None, description="Filter protections by store ID"),
):
    """
    Get all factory reset protections
    
    Optionally filter by:
    - state: Filter by protection state (Active/Inactive)
    - store_id: Filter by store ID
    """
    
    try:
        return await factory_reset_protection_service.get_factory_reset_protections(
            state=state,
            store_id=store_id
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from downstream service: {e.response.text}",
        )


@router.get(
    "/{factory_reset_protection_id}", response_model=FactoryResetProtectionResponse
)
async def get_factory_reset_protection(factory_reset_protection_id: UUID):
    frp = await factory_reset_protection_service.get_factory_reset_protection(
        factory_reset_protection_id
    )
    if not frp:
        raise HTTPException(
            status_code=404, detail="Factory reset protection not found"
        )
    return frp


@router.patch(
    "/{factory_reset_protection_id}", response_model=FactoryResetProtectionResponse
)
async def update_factory_reset_protection(
    factory_reset_protection_id: UUID, frp_update: FactoryResetProtectionUpdate
):
    updated_frp = (
        await factory_reset_protection_service.update_factory_reset_protection(
            factory_reset_protection_id, frp_update
        )
    )
    if not updated_frp:
        raise HTTPException(
            status_code=404,
            detail="Factory reset protection not found or not updated",
        )
    return updated_frp


@router.delete("/{factory_reset_protection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_factory_reset_protection(factory_reset_protection_id: UUID):
    deleted_ok = await factory_reset_protection_service.delete_factory_reset_protection(
        factory_reset_protection_id
    )
    if not deleted_ok:
        raise HTTPException(
            status_code=404, detail="Factory reset protection not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
