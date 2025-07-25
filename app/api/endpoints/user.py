from typing import List, Optional
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.auth.dependencies import get_current_user
from app.models.user import User, UserCreate, UserUpdate
from app.services import user as user_service
from app.utils.logger import get_logger

# Configurar el logger para este módulo
logger = get_logger(__name__)


router = APIRouter()


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate):
    try:
        return await user_service.create_user(user_in)
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        try:
            error_json = e.response.json()
            if "detail" in error_json:
                error_detail = error_json.get("detail")
        except Exception:
            pass

        logger.error(f"Error al crear usuario: {error_detail}", exc_info=True)
        raise HTTPException(status_code=e.response.status_code, detail=error_detail)
    except Exception as e:
        logger.error(f"Error inesperado al crear usuario: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}",
        )


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=User)
async def read_user_by_id(user_id: UUID):
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=List[User])
async def read_users(role_name: Optional[str] = None, state: Optional[str] = None, name: Optional[str] = None,
                dni: Optional[str] = None):
    try:
        return await user_service.get_users(role_name=role_name, state=state, name=name, dni=dni)
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        try:
            error_json = e.response.json()
            if "detail" in error_json:
                error_detail = error_json.get("detail")
        except Exception:
            pass

        logger.error(f"Error al obtener usuarios: {error_detail}", exc_info=True)
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from downstream service: {error_detail}",
        )
    except Exception as e:
        logger.error(f"Error inesperado al obtener usuarios: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}",
        )


@router.patch("/{user_id}", response_model=User)
async def update_user(user_id: UUID, user_in: UserUpdate):
    user = await user_service.update_user(user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID):
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
