from typing import List, Optional
from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, Response, status


from app.models.store import StoreCreate, StoreDB, StoreUpdate
from app.services import store as store_service
from app.utils.logger import get_logger

# Configurar el logger para este módulo
logger = get_logger(__name__)


router = APIRouter()


@router.post("/", response_model=StoreDB, status_code=status.HTTP_201_CREATED)
async def create_store(store_in: StoreCreate):
    """
    Crea una nueva tienda.
    """
    try:
        return await store_service.create_store(store_in)
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        try:
            error_json = e.response.json()
            if "detail" in error_json:
                error_detail = error_json.get("detail")
        except Exception:
            pass

        logger.error(f"Error al crear tienda: {error_detail}", exc_info=True)
        raise HTTPException(status_code=e.response.status_code, detail=error_detail)
    except Exception as e:
        logger.error(f"Error inesperado al crear tienda: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}",
        )


@router.get("/{store_id}", response_model=StoreDB)
async def read_store_by_id(store_id: UUID):
    """
    Obtiene una tienda por su ID.
    """
    store = await store_service.get_store(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    return store


@router.get("/", response_model=List[StoreDB])
async def read_stores(country_id: Optional[UUID] = None, plan: Optional[str] = None):
    """
    Obtiene todas las tiendas con filtros opcionales.
    """
    try:
        return await store_service.get_stores(country_id=country_id, plan=plan)
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        try:
            error_json = e.response.json()
            if "detail" in error_json:
                error_detail = error_json.get("detail")
        except Exception:
            pass

        logger.error(f"Error al obtener tiendas: {error_detail}", exc_info=True)
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from downstream service: {error_detail}",
        )
    except Exception as e:
        logger.error(f"Error inesperado al obtener tiendas: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}",
        )


@router.get("/country/{country_id}", response_model=List[StoreDB])
async def read_stores_by_country(country_id: UUID):
    """
    Obtiene todas las tiendas de un país específico.
    """
    try:
        return await store_service.get_stores_by_country(country_id)
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        try:
            error_json = e.response.json()
            if "detail" in error_json:
                error_detail = error_json.get("detail")
        except Exception:
            pass

        logger.error(
            f"Error al obtener tiendas por país: {error_detail}", exc_info=True
        )
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from downstream service: {error_detail}",
        )
    except Exception as e:
        logger.error(
            f"Error inesperado al obtener tiendas por país: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}",
        )


@router.patch("/{store_id}", response_model=StoreDB)
async def update_store(store_id: UUID, store_in: StoreUpdate):
    """
    Actualiza los datos de una tienda existente.
    """
    store = await store_service.update_store(store_id, store_in)
    if not store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    return store


@router.patch("/{store_id}/tokens", response_model=StoreDB)
async def update_store_tokens(store_id: UUID, tokens: int):
    """
    Actualiza la cantidad de tokens disponibles de una tienda.
    """
    store = await store_service.update_store_tokens(store_id, tokens)
    if not store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    return store


@router.delete("/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_store(store_id: UUID):
    """
    Elimina una tienda por su ID.
    """
    success = await store_service.delete_store(store_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
