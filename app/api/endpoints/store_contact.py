from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Query
from app.models.store_contact import (
    StoreContactCreate, 
    StoreContactDB, 
    StoreContactUpdate,
    StoreContactOut
)
from app.services import store_contact as store_contact_service

router = APIRouter()

@router.get("/by-store/{store_id}", response_model=List[StoreContactOut])
async def get_contacts_for_store(
    store_id: UUID,
    categories: Optional[List[str]] = Query(None, description="Filter contacts by categories")
):
    try:
        return await store_contact_service.get_store_contacts(store_id=store_id, categories=categories)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contacts", response_model=StoreContactDB, status_code=status.HTTP_201_CREATED)
async def create_new_contact(contact_in: StoreContactCreate):
    contact = await store_contact_service.create_store_contact(contact_in)
    if not contact:
        raise HTTPException(status_code=400, detail="Contact could not be created.")
    return contact

@router.put("/contacts/{contact_id}", response_model=StoreContactDB)
async def update_existing_contact(contact_id: UUID, contact_in: StoreContactUpdate):
    contact = await store_contact_service.update_store_contact(contact_id, contact_in)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found.")
    return contact

@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_contact(contact_id: UUID):
    success = await store_contact_service.delete_store_contact(contact_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found.")
