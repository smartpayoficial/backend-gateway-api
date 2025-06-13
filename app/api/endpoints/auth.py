import os

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.auth.security import create_access_token, decode_access_token, verify_password

router = APIRouter()


class RefreshTokenIn(BaseModel):
    refresh_token: str


USER_SVC_URL = os.getenv("USER_SVC_URL") or os.getenv("DB_API", "http://localhost:8002")
# Prefijo común del servicio de usuarios
USER_API_PREFIX = "/api/v1"
# Header requerido para rutas internas
INTERNAL_HDR = {"X-Internal-Request": "true"}


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/auth/login", response_model=TokenOut)
async def login(data: LoginIn):
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{USER_API_PREFIX}/users/by-username/{data.username}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    user = resp.json()
    # Determinar estado activo (acepta is_active bool o state="Active")
    is_active = user.get("is_active")
    if is_active is None:
        is_active = str(user.get("state", "")).lower() == "active"

    password_valid = verify_password(data.password, user["password_hash"])

    if not is_active or not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas"
        )

    token_data = {
        "sub": user["user_id"],
        "username": user["username"],
        "role": user["role"]["name"],
    }
    token = create_access_token(token_data)
    # Crear refresh_token con expiración más larga y claim especial
    refresh_token = create_access_token(
        {**token_data, "type": "refresh"}, expires_minutes=60 * 24 * 7
    )  # 7 días
    return {"access_token": token, "refresh_token": refresh_token}


@router.post("/auth/refresh", response_model=TokenOut)
async def refresh_token(data: RefreshTokenIn):
    try:
        payload = decode_access_token(data.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    # Crear nuevos tokens
    token_data = {
        "sub": payload["sub"],
        "username": payload["username"],
        "role": payload["role"],
    }
    access_token = create_access_token(token_data)
    new_refresh_token = create_access_token(
        {**token_data, "type": "refresh"}, expires_minutes=60 * 24 * 7
    )
    return {"access_token": access_token, "refresh_token": new_refresh_token}
