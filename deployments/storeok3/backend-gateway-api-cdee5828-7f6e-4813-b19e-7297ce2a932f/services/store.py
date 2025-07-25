import os
from typing import List, Optional
from uuid import UUID

import httpx

from app.models.store import StoreCreate, StoreDB, StoreUpdate
from app.utils.logger import get_logger

# Configurar el logger para este módulo
logger = get_logger(__name__)

# El servicio de tiendas está en el mismo servicio de DB que los usuarios
# Usamos la variable de entorno DB_API que está definida en el docker-compose
DB_API_URL = os.getenv("DB_API", "http://smartpay-db-api:8002")
STORE_API_URL = f"{DB_API_URL}/api/v1/stores"


async def create_store(store_in: StoreCreate) -> StoreDB:
    """
    Crea una nueva tienda en la base de datos.

    Args:
        store_in: Datos de la tienda a crear

    Returns:
        dict: La tienda creada con todos sus datos en formato diccionario

    Raises:
        HTTPException: Si ocurre un error en la comunicación con el servicio de DB
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{STORE_API_URL}/", json=store_in.model_dump(mode="json")
            )
            response.raise_for_status()  # Will raise an exception for 4xx/5xx responses
            store_data = response.json()
            store = StoreDB.model_validate(store_data)
            return store
    except httpx.HTTPStatusError as e:
        logger.error(f"Error al crear tienda: {e.response.text}", exc_info=True)
        # Re-lanzamos la excepción para que el endpoint pueda manejarla
        raise
    except Exception as e:
        logger.error(f"Error inesperado al crear tienda: {str(e)}", exc_info=True)
        raise


async def get_store(store_id: UUID):
    """
    Obtiene una tienda y transforma la respuesta al formato exacto requerido.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{STORE_API_URL}/{store_id}?expand=country,admin")
            if response.status_code == 200:
                store_data = response.json()
                # Convertimos a StoreDB para validar y luego a dict para retornar
                # Esto asegura que la estructura sea exactamente la que necesitamos
                store = StoreDB.model_validate(store_data)
                # Serializamos excluyendo la propiedad admin_id para evitar errores
                result = store.model_dump(mode="json", exclude={"admin_id"})
                # Agregamos manualmente el admin_id si existe
                if store.admin:
                    result["admin_id"] = str(store.admin.user_id)
                return result
            else:
                return None
    except Exception as e:
        logger.error(f"Error al obtener tienda {store_id}: {str(e)}")
        return None


async def get_stores(
    country_id: Optional[UUID] = None, plan: Optional[str] = None
) -> List[dict]:
    """
    Obtiene tiendas con transformación al formato exacto requerido.
    """
    params = {"expand": "country,admin"}
    if country_id:
        params["country_id"] = str(country_id)
    if plan:
        params["plan"] = plan

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{STORE_API_URL}/", params=params)
            response.raise_for_status()
            
            stores = []
            for store_data in response.json():
                # Usar Pydantic para validar y transformar
                store = StoreDB.model_validate(store_data)
                # Convertir a diccionario para mantener el formato exacto requerido
                # Excluimos la propiedad admin_id que causa problemas de serialización
                store_dict = store.model_dump(mode="json", exclude={"admin_id"})
                # Agregamos manualmente el admin_id si existe
                if store.admin:
                    store_dict["admin_id"] = str(store.admin.user_id)
                stores.append(store_dict)
            return stores
    except Exception as e:
        logger.error(f"Error al obtener tiendas: {str(e)}")
        raise


async def update_store(store_id: UUID, store_in: StoreUpdate) -> Optional[dict]:
    """
    Actualiza los datos de una tienda existente.

    Args:
        store_id: ID de la tienda a actualizar
        store_in: Datos a actualizar

    Returns:
        dict: La tienda actualizada o None si no existe
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{STORE_API_URL}/{store_id}",
                json=store_in.model_dump(mode="json", exclude_unset=True),
            )
            # Aceptar tanto 200 (con contenido) como 204 (sin contenido) como respuestas exitosas
            if response.status_code == 200:
                store_data = response.json()
                store = StoreDB.model_validate(store_data)
                # Serializamos excluyendo la propiedad admin_id para evitar errores
                result = store.model_dump(mode="json", exclude={"admin_id"})
                # Agregamos manualmente el admin_id si existe
                if store.admin:
                    result["admin_id"] = str(store.admin.user_id)
                return result
            elif response.status_code == 204:
                # Para 204 No Content, obtenemos la tienda actualizada con una llamada adicional
                logger.info(
                    f"Recibido 204 No Content al actualizar tienda {store_id}, obteniendo datos actualizados"
                )
                return await get_store(store_id)
            return None
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Error al actualizar tienda {store_id}: {e.response.text}", exc_info=True
        )
        return None
    except Exception as e:
        logger.error(
            f"Error inesperado al actualizar tienda {store_id}: {str(e)}", exc_info=True
        )
        return None


async def delete_store(store_id: UUID) -> bool:
    """
    Elimina una tienda por su ID.

    Args:
        store_id: ID de la tienda a eliminar

    Returns:
        bool: True si la tienda fue eliminada, False en caso contrario
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{STORE_API_URL}/{store_id}")
            return response.status_code == 204
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Error al eliminar tienda {store_id}: {e.response.text}", exc_info=True
        )
        return False
    except Exception as e:
        logger.error(
            f"Error inesperado al eliminar tienda {store_id}: {str(e)}", exc_info=True
        )
        return False


async def update_store_tokens(store_id: UUID, tokens: int) -> Optional[dict]:
    """
    Actualiza la cantidad de tokens disponibles de una tienda.

    Args:
        store_id: ID de la tienda
        tokens: Nueva cantidad de tokens

    Returns:
        dict: La tienda actualizada o None si no existe
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{STORE_API_URL}/{store_id}/tokens",
                json={"tokens_disponibles": tokens},
            )
            # Aceptar tanto 200 (con contenido) como 204 (sin contenido) como respuestas exitosas
            if response.status_code == 200:
                store_data = response.json()
                store = StoreDB.model_validate(store_data)
                # Serializamos excluyendo la propiedad admin_id para evitar errores
                result = store.model_dump(mode="json", exclude={"admin_id"})
                # Agregamos manualmente el admin_id si existe
                if store.admin:
                    result["admin_id"] = str(store.admin.user_id)
                return result
            elif response.status_code == 204:
                # Para 204 No Content, obtenemos la tienda actualizada con una llamada adicional
                logger.info(
                    f"Recibido 204 No Content al actualizar tokens de tienda {store_id}, obteniendo datos actualizados"
                )
                return await get_store(store_id)
            return None
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Error al actualizar tokens de tienda {store_id}: {e.response.text}",
            exc_info=True,
        )
        return None
    except Exception as e:
        logger.error(
            f"Error inesperado al actualizar tokens de tienda {store_id}: {str(e)}",
            exc_info=True,
        )
        return None


async def get_stores_by_country(country_id: UUID) -> List[StoreDB]:
    """
    Obtiene todas las tiendas de un país específico.

    Args:
        country_id: ID del país

    Returns:
        List[StoreDB]: Lista de tiendas del país
    """
    # Utilizar get_stores con el parámetro expand=country ya configurado
    return await get_stores(country_id=country_id)
