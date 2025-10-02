import os
from typing import List, Optional
from uuid import UUID
import httpx
from app.models.account_type import AccountTypeDB

USER_SVC_URL = os.getenv("USER_SVC_URL", "http://localhost:8002")

async def get_account_types(country_id: Optional[UUID] = None, categories: Optional[List[str]] = None) -> List[AccountTypeDB]:
    params = {}
    if country_id:
        params["country_id"] = str(country_id)
    if categories:
        params["categories"] = categories

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SVC_URL}/api/v1/account-types/", params=params)
        response.raise_for_status()
        return [AccountTypeDB(**item) for item in response.json()]

async def get_account_type_categories() -> List[str]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SVC_URL}/api/v1/account-types/categories")
        response.raise_for_status()
        return response.json()
