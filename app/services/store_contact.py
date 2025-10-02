import os
from typing import List, Optional
from uuid import UUID
import httpx
from app.models.store_contact import (
    StoreContactCreate, 
    StoreContactDB, 
    StoreContactUpdate, 
    StoreContactOut
)

USER_SVC_URL = os.getenv("USER_SVC_URL", "http://localhost:8002")

async def get_store_contacts(store_id: UUID, categories: Optional[List[str]] = None) -> List[StoreContactOut]:
    params = [
        ("expand", "account_type")
    ]
    if categories:
        for category in categories:
            params.append(("categories", category))

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{USER_SVC_URL}/api/v1/store-contacts/by-store/{store_id}",
            params=params
        )
        response.raise_for_status()
        return [StoreContactOut(**item) for item in response.json()]

async def create_store_contact(contact_in: StoreContactCreate) -> Optional[StoreContactDB]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{USER_SVC_URL}/api/v1/store-contacts/", json=contact_in.model_dump(mode="json")
        )
        if response.status_code == 201:
            return StoreContactDB(**response.json())
        return None

async def update_store_contact(contact_id: UUID, contact_in: StoreContactUpdate) -> Optional[StoreContactDB]:
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{USER_SVC_URL}/api/v1/store-contacts/{contact_id}",
            json=contact_in.model_dump(mode="json", exclude_unset=True),
        )
        if response.status_code == 200:
            return StoreContactDB(**response.json())
        return None

async def delete_store_contact(contact_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{USER_SVC_URL}/api/v1/store-contacts/{contact_id}")
        return response.status_code == 204
