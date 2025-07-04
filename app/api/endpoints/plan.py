import os
import shutil
from typing import List
from uuid import UUID

import httpx
from fastapi import APIRouter, File, Form, HTTPException, Path, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse

from app.models.plan import Plan, PlanCreate, PlanDB, PlanRaw, PlanUpdate
from app.services import plan as plan_service

router = APIRouter()

UPLOADS_DIR = "uploads/"


@router.post("/upload-pdf/", status_code=status.HTTP_200_OK)
async def upload_plan_pdf(plan_id: str = Form(...), file: UploadFile = File(...)):
    if not file.content_type == "application/pdf":
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only PDFs are allowed."
        )

    # Create the uploads directory if it doesn't exist
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    file_path = os.path.join(UPLOADS_DIR, f"{plan_id}.pdf")

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename} as {plan_id}.pdf"}


@router.get("/download-pdf/{plan_id}")
async def download_plan_pdf(plan_id: str):
    file_path = os.path.join(UPLOADS_DIR, f"{plan_id}.pdf")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF not found for this plan_id.")

    return FileResponse(
        path=file_path, media_type="application/pdf", filename=f"{plan_id}.pdf"
    )


@router.post("/", response_model=Plan, status_code=status.HTTP_201_CREATED)
async def create_plan(new_plan: PlanCreate):
    plan = await plan_service.create_plan(new_plan)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan could not be created.",
        )
    return plan


@router.get("/", response_model=List[PlanRaw], status_code=status.HTTP_200_OK)
async def get_all_plans():
    try:
        return await plan_service.get_all_plans()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from downstream service: {e.response.text}",
        )


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
