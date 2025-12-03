from typing import Dict, List, Optional
from uuid import UUID

import httpx
import os
from fastapi import APIRouter, HTTPException, Path, Query, status

from app.models.television import Television, TelevisionCreate, TelevisionUpdate

# Imports for Location
from app.services import television as television_service


router = APIRouter()


# --- Television Endpoints ---
@router.post("/", response_model=Television, status_code=status.HTTP_201_CREATED)
async def create_television(television_in: TelevisionCreate):
    television = await television_service.create_television(television_in)
    if not television:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device could not be created.",
        )
    return television


@router.get("/", response_model=List[Television])
async def get_all_televisions(
    enrollment_id: Optional[str] = Query(None), user_id: Optional[UUID] = Query(None)
):
    try:
        return await television_service.get_televisions(
            enrollment_id=enrollment_id, user_id=user_id
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from downstream service: {e.response.text}",
        )


@router.get("/count", response_model=Dict[str, int])
async def get_television_count():
    try:
        count = await television_service.get_television_count()
        return {"count": count}
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from downstream service: {e.response.text}",
        )


@router.get("/{television_id}", response_model=Television)
async def get_television_by_id(television_id: UUID = Path(...)):
    television = await television_service.get_television(television_id)
    if not television:
        raise HTTPException(status_code=404, detail="Television not found")
    return television


@router.patch("/{television_id}", response_model=Television)
async def update_television(television_id: UUID, television_in: TelevisionUpdate):
    television = await television_service.update_television(television_id, television_in)
    if not television:
        raise HTTPException(status_code=404, detail="Television not found")
    return television


@router.delete("/{television_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_television(television_id: UUID):
    success = await television_service.delete_television(television_id)
    if not success:
        raise HTTPException(status_code=404, detail="Television not found")
