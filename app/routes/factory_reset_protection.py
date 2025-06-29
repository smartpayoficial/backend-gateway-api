from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.models.factory_reset_protection import FactoryResetProtectionResponse, FactoryResetProtectionCreate, FactoryResetProtectionState, FactoryResetProtectionUpdate
from app.servicios import factory_reset_protection as factory_reset_protection_service

router = APIRouter(tags=["factoryResetProtection"])

@router.post("/", response_model=FactoryResetProtectionResponse)
async def create_factory_reset_protection(payment: FactoryResetProtectionCreate):  
    return await factory_reset_protection_service.create_factory_reset_protection(payment)


@router.get("/", response_model=List[FactoryResetProtectionResponse])
async def get_factory_reset_protections(
    state: Optional[FactoryResetProtectionState] = Query(None)
):
    return await factory_reset_protection_service.get_factory_reset_protections(state=state)


@router.get("/{factory_reset_protection_id}", response_model=FactoryResetProtectionResponse)
async def get_factory_reset_protection(factory_reset_protection_id: UUID):
    payment = await factory_reset_protection_service.get_factory_reset_protection(factory_reset_protection_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.patch("/{factory_reset_protection_id}", response_model=FactoryResetProtectionResponse)
async def update_factory_reset_protection(factory_reset_protection_id: UUID, factory: FactoryResetProtectionUpdate):
    updated = await factory_reset_protection_service.update_factory_reset_protection(factory_reset_protection_id, factory)
    if not updated:
        raise HTTPException(status_code=404, detail="Payment not found or not updated")
    return updated


@router.delete("/{factory_reset_protection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(factory_reset_protection_id: UUID):
    deleted = await factory_reset_protection_service.delete_factory_protection(factory_reset_protection_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Payment not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
