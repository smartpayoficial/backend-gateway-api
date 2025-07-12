import os
from typing import List, Optional
from uuid import UUID

import httpx

from app.models.action import ActionCreate, ActionResponse, ActionUpdate

# Obtener la URL del servicio de base de datos de las variables de entorno
DB_API_URL = os.getenv("DB_API", "http://localhost:8002")
API_PREFIX = "/api/v1"
INTERNAL_HDR = {"X-Internal-Request": "true"}


async def create_action(action_in: ActionCreate) -> Optional[ActionResponse]:
    """
    Envía una solicitud para crear un nuevo registro de acción al servicio de base de datos.
    """
    # Construir la URL completa para el endpoint de creación de acciones
    # Asumimos que el endpoint en el servicio DB es /api/v1/actions
    url = f"{DB_API_URL}{API_PREFIX}/actions"

    async with httpx.AsyncClient() as client:
        try:
            # Enviar la solicitud POST con los datos de la acción en formato JSON
            response = await client.post(
                url, json=action_in.model_dump(mode="json"), headers=INTERNAL_HDR
            )

            # Si la solicitud no fue exitosa (e.g., 4xx, 5xx), lanzar una excepción
            response.raise_for_status()

            # Si la creación fue exitosa (201 Created), devolver el objeto de la acción creado
            return ActionResponse(**response.json())

        except httpx.HTTPStatusError as e:
            # Propagar el error HTTP para que el endpoint que llama pueda manejarlo
            print(f"Error al crear la acción en el servicio DB: {e.response.text}")
            raise e
        except Exception as e:
            # Manejar otros errores (e.g., problemas de conexión)
            print(f"Ocurrió un error inesperado al contactar el servicio DB: {url}")
            return None


async def get_actions(
    device_id: Optional[UUID] = None, state: Optional[str] = None
) -> List[ActionResponse]:
    """
    Obtiene una lista de acciones desde el servicio de base de datos, con filtros opcionales.
    """
    url = f"{DB_API_URL}{API_PREFIX}/actions"
    params = {}
    if device_id:
        params["device_id"] = str(device_id)
    if state:
        params["state"] = state

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, headers=INTERNAL_HDR)
            response.raise_for_status()
            return [ActionResponse(**action) for action in response.json()]
        except httpx.HTTPStatusError as e:
            print(f"Error al obtener las acciones del servicio DB: {e.response.text}")
            raise e
        except Exception as e:
            print(f"Ocurrió un error inesperado al contactar el servicio DB: {url}")
            return []


async def get_action(action_id: UUID) -> Optional[ActionResponse]:
    """
    Obtiene una única acción por su ID.
    """
    url = f"{DB_API_URL}{API_PREFIX}/actions/{action_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=INTERNAL_HDR)
            response.raise_for_status()
            return ActionResponse(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            print(f"Error al obtener la acción {action_id}: {e.response.text}")
            raise e
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")
            return None


async def update_action(
    action_id: UUID, action_in: ActionUpdate
) -> Optional[ActionResponse]:
    """
    Actualiza una acción existente.
    """
    url = f"{DB_API_URL}{API_PREFIX}/actions/{action_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(
                url, json=action_in.model_dump(mode='json', exclude_unset=True), headers=INTERNAL_HDR
            )
            response.raise_for_status()
            return ActionResponse(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            print(f"Error al actualizar la acción {action_id}: {e.response.text}")
            raise e
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")
            return None


async def delete_action(action_id: UUID) -> bool:
    """
    Elimina una acción por su ID.
    """
    url = f"{DB_API_URL}{API_PREFIX}/actions/{action_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(url, headers=INTERNAL_HDR)
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return False
            print(f"Error al eliminar la acción {action_id}: {e.response.text}")
            raise e
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")
            return False
