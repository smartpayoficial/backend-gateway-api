from typing import List
from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, status

from app.models.enrolment import EnrolmentCreate, EnrolmentDB
from app.services import enrolment as enrolment_service

router = APIRouter()


@router.get("/", response_model=List[EnrolmentDB])
async def list_enrolments():
    """Lista todas las inscripciones (enrolments)."""
    try:
        return await enrolment_service.get_enrolments()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from downstream service: {e.response.text}",
        )


@router.get("/{enrolment_id}", response_model=EnrolmentDB)
async def get_enrolment(enrolment_id: UUID):
    """Obtiene una inscripción por su ID."""
    enrol = await enrolment_service.get_enrolment(enrolment_id)
    if not enrol:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    return enrol


@router.post("/", response_model=EnrolmentDB, status_code=status.HTTP_201_CREATED)
async def create_enrolment(enrolment: EnrolmentCreate):
    """Crea una nueva inscripción."""
    new_enrolment = await enrolment_service.create_enrolment(enrolment)
    if not new_enrolment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enrolment could not be created.",
        )
    return new_enrolment


@router.delete("/{enrolment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrolment(enrolment_id: UUID):
    """Elimina una inscripción por su ID."""
    ok = await enrolment_service.delete_enrolment(enrolment_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
