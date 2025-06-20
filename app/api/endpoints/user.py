import os
from typing import Optional
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.models.user import UserOut, UserUpdate
from app.servicios import user as user_service

router = APIRouter()

USER_SVC_URL = os.getenv("USER_SVC_URL") or os.getenv("DB_API", "http://localhost:8002")
USER_API_PREFIX = "/api/v1"
INTERNAL_HDR = {"X-Internal-Request": "true"}


class UserCreateIn(BaseModel):
    city_id: str
    dni: str = Field(..., max_length=15)
    first_name: str
    middle_name: str | None = None
    last_name: str
    second_last_name: str | None = None
    email: str
    prefix: str
    phone: str
    address: str
    username: str
    password: str
    role_id: str
    state: str = "Active"


@router.post("/users", response_model=UserOut, status_code=201)
async def create_user(data: UserCreateIn):
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{USER_API_PREFIX}/users"
        resp = await client.post(url, headers=INTERNAL_HDR, json=data.dict())
    if resp.status_code != 201:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()


@router.patch("/users/{user_id}", response_model=UserOut)
async def update_user(user_id: UUID, data: UserUpdate):
    user = await user_service.update_user(user_id, data)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: UUID):
    ok = await user_service.delete_user(user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return Response(status_code=204)


@router.get("/users/me", response_model=UserOut)
async def get_me(current_user: UserOut = Depends(get_current_user)):
    """
    Retorna la información del usuario autenticado usando el token de acceso.
    """
    return current_user


@router.get("/users", response_model=list[UserOut])
async def get_all_users(role_name: Optional[str] = None, state: Optional[str] = None):
    params = {}
    if role_name:
        params["role_name"] = role_name
    if state:
        params["state"] = state
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{USER_API_PREFIX}/users"
        resp = await client.get(url, headers=INTERNAL_HDR, params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()
