from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query
from app.models.account_type import AccountTypeDB
from app.services import account_type as account_type_service

router = APIRouter()

@router.get("/", response_model=List[AccountTypeDB])
async def get_all_account_types(
    country_id: Optional[UUID] = None,
    categories: Optional[List[str]] = Query(None)
):
    try:
        return await account_type_service.get_account_types(country_id=country_id, categories=categories)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories", response_model=List[str])
async def get_account_type_categories():
    try:
        return await account_type_service.get_account_type_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
