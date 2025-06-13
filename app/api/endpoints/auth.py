import os

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.auth.security import create_access_token, verify_password

router = APIRouter()
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

    token = create_access_token(
        {
            "sub": user["user_id"],
            "username": user["username"],
            "role": user["role"]["name"],
        }
    )
    return {"access_token": token}
