from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, status
from fastapi.responses import JSONResponse

from app.models.plan import PlanCreate, PlanDB, PlanRaw, PlanUpdate
from app.servicios import plan as plan_service

router = APIRouter()


@router.post("/", response_model=PlanDB, status_code=status.HTTP_201_CREATED)
async def create_plan(new_plan: PlanCreate):
    return await plan_service.create_plan(new_plan)


@router.get("/", response_model=List[PlanRaw], status_code=status.HTTP_200_OK)
async def get_all_plans():
    return await plan_service.get_all_plans()


@router.get("/{plan_id}", response_model=PlanRaw, status_code=status.HTTP_200_OK)
async def get_plan_by_id(plan_id: UUID = Path(...)):
    plan = await plan_service.get_plan_by_id(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.patch("/{plan_id}", response_model=PlanDB, status_code=status.HTTP_200_OK)
async def update_plan(plan_id: UUID, plan_update: PlanUpdate):
    updated = await plan_service.update_plan(plan_id, plan_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Plan not found")
    return updated


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(plan_id: UUID = Path(...)):
    deleted = await plan_service.delete_plan(plan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Plan not found")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
