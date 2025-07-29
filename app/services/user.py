import os
from typing import List, Optional
from uuid import UUID

import httpx

from app.models.user import User, UserCreate, UserUpdate
from app.utils.logger import get_logger

# Configurar el logger para este módulo
logger = get_logger(__name__)

USER_SVC_URL = os.getenv("USER_SVC_URL", "http://localhost:8002")
USER_API_URL = f"{USER_SVC_URL}/api/v1/users"

# Configuración de timeout para las solicitudes HTTP
TIMEOUT_SECONDS = 30.0


async def create_user(user_in: UserCreate) -> User:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.post(
                f"{USER_API_URL}/", json=user_in.model_dump(mode="json")
            )
            response.raise_for_status()  # Will raise an exception for 4xx/5xx responses
            return User(**response.json())
    except httpx.HTTPStatusError as e:
        logger.error(f"Error al crear usuario: {e.response.text}", exc_info=True)
        # Re-lanzamos la excepción para que el endpoint pueda manejarla
        raise
    except Exception as e:
        logger.error(f"Error inesperado al crear usuario: {str(e)}", exc_info=True)
        raise


async def get_user(user_id: UUID) -> Optional[User]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(f"{USER_API_URL}/{user_id}")
            if response.status_code == 200:
                return User(**response.json())
            return None
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Error al obtener usuario {user_id}: {e.response.text}", exc_info=True
        )
        return None
    except Exception as e:
        logger.error(
            f"Error inesperado al obtener usuario {user_id}: {str(e)}", exc_info=True
        )
        return None


async def get_users(
    role_name: Optional[str] = None, state: Optional[str] = None, name: Optional[str] = None,
    dni: Optional[str] = None, store: Optional[UUID] = None
) -> List[User]:
    params = {}
    if role_name:
        params["role_name"] = role_name
    if state:
        params["state"] = state
    if name:
        params["name"] = name
    if dni:
        params["dni"] = dni
    if store:
        params["store_id"] = str(store)

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(f"{USER_API_URL}/", params=params)
            response.raise_for_status()
            return [User(**item) for item in response.json()]
    except httpx.HTTPStatusError as e:
        logger.error(f"Error al obtener usuarios: {e.response.text}", exc_info=True)
        # Re-lanzamos la excepción para que el endpoint pueda manejarla
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener usuarios: {str(e)}", exc_info=True)
        raise


async def update_user(user_id: UUID, user_in: UserUpdate) -> Optional[User]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.patch(
                f"{USER_API_URL}/{user_id}",
                json=user_in.model_dump(mode="json", exclude_none=True),
            )
            response.raise_for_status()  # Lanza una excepción para errores 4xx/5xx
            return User(**response.json())
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Error al actualizar usuario {user_id}: {e.response.text}", exc_info=True
        )
        raise
    except Exception as e:
        logger.error(
            f"Error inesperado al actualizar usuario {user_id}: {str(e)}", exc_info=True
        )
        return None


async def delete_user(user_id: UUID) -> bool:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.delete(f"{USER_API_URL}/{user_id}")
            return response.status_code == 204
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Error al eliminar usuario {user_id}: {e.response.text}", exc_info=True
        )
        return False
    except Exception as e:
        logger.error(
            f"Error inesperado al eliminar usuario {user_id}: {str(e)}", exc_info=True
        )
        return False
