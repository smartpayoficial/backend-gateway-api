from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.models.enrolment import EnrolmentCreate, EnrolmentDB
from app.servicios import enrolment as enrolment_service

router = APIRouter()


@router.get("/", response_model=List[EnrolmentDB])
async def list_enrolments():
    """Lista todas las inscripciones (enrolments)."""
    return await enrolment_service.get_enrolments()


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
    return await enrolment_service.create_enrolment(enrolment)


@router.delete("/{enrolment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrolment(enrolment_id: UUID):
    """Elimina una inscripción por su ID."""
    ok = await enrolment_service.delete_enrolment(enrolment_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
