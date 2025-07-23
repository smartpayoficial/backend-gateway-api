from typing import List, Optional
from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, Response, status

from app.models.store import StoreCreate, StoreDB, StoreUpdate
from app.services import store as store_service
from app.services.deployment import deployment_service
from app.utils.logger import get_logger

# Configurar el logger para este módulo
logger = get_logger(__name__)


router = APIRouter()


# Endpoint eliminado - ahora se usa create_store (anteriormente create_and_deploy_store)


@router.get("/{store_id}", response_model=StoreDB)
async def read_store_by_id(store_id: UUID):
    """
    Obtiene una tienda por su ID incluyendo la entidad completa del admin cuando esté disponible.
    """
    store = await store_service.get_store(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    return store


@router.get("/", response_model=List[StoreDB])
async def read_stores(country_id: Optional[UUID] = None, plan: Optional[str] = None):
    """
    Obtiene todas las tiendas con filtros opcionales, incluyendo la entidad completa del admin cuando esté disponible.
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
    Obtiene todas las tiendas de un país específico, incluyendo la entidad completa del admin cuando esté disponible.
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


@router.post("/deploy", status_code=status.HTTP_201_CREATED)
async def create_and_deploy_store(store_in: StoreCreate):
    """
    Crea y despliega una nueva tienda, manejando correctamente la entidad admin cuando esté presente.
    """
    try:
        # Crear la tienda (admin_id se maneja automáticamente desde StoreCreate)
        store = await store_service.create_store(store_in)
        if not store:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo crear la tienda"
            )

        store_id = store.id
        
        # Realizar el deployment
        deployment_info = await deployment_service.deploy_store(store_id)
        if not deployment_info:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo desplegar la tienda"
            )

        # Obtener la tienda con todos los datos actualizados (incluyendo admin completo si existe)
        full_store = await store_service.get_store(store_id)
        
        return {
            "store": full_store,
            "deployment": {
                "back_link": deployment_info["back_link"],
                "db_link": deployment_info["db_link"],
                "ports": deployment_info["ports"],
                "status": "deployed"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en deployment de tienda: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado durante el deployment: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_store(store_in: StoreCreate):
    """
    Crea una nueva tienda y despliega automáticamente una versión del backend y DB.
    
    Este endpoint:
    1. Crea la tienda con los datos proporcionados
    2. Crea directorios únicos para el backend y DB de la tienda
    3. Copia los archivos necesarios
    4. Configura puertos únicos para evitar conflictos
    5. Levanta los servicios usando Docker Compose
    6. Actualiza la tienda con los links generados
    
    Args:
        store_in: Datos de la tienda a crear (nombre, country_id, plan, tokens_disponibles)
        
    Returns:
        Información de la tienda creada y su deployment incluyendo links y puertos asignados
    """
    try:
        # Crear la tienda primero
        logger.info(f"Creando nueva tienda: {store_in.nombre}")
        
        try:
            store = await store_service.create_store(store_in)
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
                detail=f"Error inesperado al crear tienda: {str(e)}"
            )
        
        store_id = store.id
        logger.info(f"Tienda creada exitosamente con ID: {store_id}")
        logger.info(f"Iniciando deployment para tienda {store_id}")
        
        # Realizar el deployment
        deployment_info = await deployment_service.deploy_store(store_id)
        
        if not deployment_info:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error durante el proceso de deployment"
            )
        
        # Actualizar la tienda con los links generados
        from app.models.store import StoreUpdate
        store_update = StoreUpdate(
            back_link=deployment_info["back_link"],
            db_link=deployment_info["db_link"]
        )
        
        updated_store = await store_service.update_store(store_id, store_update)
        if not updated_store:
            logger.error(f"Error actualizando tienda {store_id} con links de deployment")
            # No fallar el deployment por esto, solo log
        
        logger.info(f"Deployment completado exitosamente para tienda {store_id}")
        
        return {
            "message": "Tienda creada y deployment completado exitosamente",
            "store": {
                "id": str(store.id),
                "nombre": store.nombre,
                "country_id": str(store.country_id),
                "plan": store.plan,
                "tokens_disponibles": store.tokens_disponibles,
                "created_at": store.created_at.isoformat(),
                "back_link": deployment_info["back_link"],
                "db_link": deployment_info["db_link"]
            },
            "deployment": {
                "back_link": deployment_info["back_link"],
                "db_link": deployment_info["db_link"],
                "ports": deployment_info["ports"],
                "status": "deployed"
            }
        }
        
    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        raise
    except Exception as e:
        logger.error(f"Error inesperado en deployment de tienda {store_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado durante el deployment: {str(e)}"
        )


@router.post("/{store_id}/deploy", status_code=status.HTTP_200_OK)
async def deploy_existing_store(store_id: UUID):
    """
    Despliega una tienda existente, incluyendo la entidad completa del admin si está disponible.
    """
    try:
        # Verificar que la tienda existe y obtener datos actuales
        store = await store_service.get_store(store_id)
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tienda no encontrada"
            )

        # Realizar el deployment
        deployment_info = await deployment_service.deploy_store(store_id)
        if not deployment_info:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo desplegar la tienda"
            )

        # Obtener la tienda con todos los datos actualizados (incluyendo admin completo)
        full_store = await store_service.get_store(store_id)
        
        return {
            "store": full_store,
            "deployment": {
                "back_link": deployment_info["back_link"],
                "db_link": deployment_info["db_link"],
                "ports": deployment_info["ports"],
                "status": "deployed"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en deployment de tienda {store_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado durante el deployment: {str(e)}"
        )


@router.get("/{store_id}/deploy/status", status_code=status.HTTP_200_OK)
async def get_deployment_status(store_id: UUID):
    """
    Obtiene el estado actual del deployment de una tienda.
    
    Args:
        store_id: ID de la tienda
        
    Returns:
        Estado del deployment incluyendo si está corriendo, puertos, etc.
    """
    try:
        # Verificar que la tienda existe
        store = await store_service.get_store(store_id)
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tienda no encontrada"
            )
        
        # Obtener estado del deployment
        deployment_status = await deployment_service.get_deployment_status(store_id)
        
        return deployment_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estado de deployment para tienda {store_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estado del deployment: {str(e)}"
        )


@router.delete("/{store_id}/deploy", status_code=status.HTTP_200_OK)
async def undeploy_store(store_id: UUID):
    """
    Detiene y elimina completamente el deployment de una tienda.
    
    Este endpoint:
    1. Verifica que la tienda existe
    2. Detiene todos los servicios Docker asociados
    3. Elimina los archivos de deployment
    4. Limpia los links de la tienda en la base de datos
    
    Args:
        store_id: ID de la tienda
        
    Returns:
        Confirmación del undeploy
    """
    try:
        # Verificar que la tienda existe
        store = await store_service.get_store(store_id)
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tienda no encontrada"
            )
        
        logger.info(f"Iniciando undeploy para tienda {store_id}")
        
        # Realizar el undeploy
        success = await deployment_service.undeploy_store(store_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error durante el proceso de undeploy"
            )
        
        # Limpiar los links de la tienda
        from app.models.store import StoreUpdate
        store_update = StoreUpdate(
            back_link=None,
            db_link=None
        )
        
        updated_store = await store_service.update_store(store_id, store_update)
        if not updated_store:
            logger.error(f"Error limpiando links de tienda {store_id} después del undeploy")
            # No fallar el undeploy por esto, solo log
        
        logger.info(f"Undeploy completado exitosamente para tienda {store_id}")
        
        return {
            "message": "Undeploy completado exitosamente",
            "store_id": str(store_id),
            "status": "undeployed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en undeploy de tienda {store_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado durante el undeploy: {str(e)}"
        )
