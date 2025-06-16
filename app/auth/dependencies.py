import os

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.security import decode_access_token
from app.models.user import UserOut
from app.models.user import UserOut as EndpointUserOut

USER_SVC_URL = os.getenv("USER_SVC_URL") or os.getenv("DB_API", "http://localhost:8002")
USER_API_PREFIX = "/api/v1"
INTERNAL_HDR = {"X-Internal-Request": "true"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> EndpointUserOut:
    payload = decode_access_token(token)
    user_id = payload.get("sub")  # type: ignore[assignment]
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token sin sub")

    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{USER_API_PREFIX}/users/{user_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Usuario no existe")

    data = resp.json()
    is_active = data.get("is_active")
    if is_active is None:
        is_active = str(data.get("state", "")).lower() == "active"

    # Obtener el rol de forma robusta
    # Construir el modelo UserOut completo para endpoints
    # Validar y asignar valores por defecto a todos los campos requeridos por UserOut (endpoints)
    user = EndpointUserOut(
        user_id=data.get("user_id", ""),
        city=data.get("city") if data.get("city") is not None else {},
        dni=data.get("dni", ""),
        first_name=data.get("first_name", ""),
        middle_name=data.get("middle_name"),
        last_name=data.get("last_name", ""),
        second_last_name=data.get("second_last_name"),
        email=data.get("email", ""),
        prefix=data.get("prefix", ""),
        phone=data.get("phone", ""),
        address=data.get("address", ""),
        username=data.get("username", ""),
        state=data.get("state", ""),
        created_at=data.get("created_at"),
        updated_at=data.get("updated_at"),
    )
    return user


def role_checker(allowed: list[str]):
    async def _checker(user: UserOut = Depends(get_current_user)):
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Permiso denegado"
            )
        return user

    return _checker
