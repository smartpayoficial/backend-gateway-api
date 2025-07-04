import os
from uuid import UUID

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.security import decode_access_token
from app.models.user import User

USER_SVC_URL = os.getenv("USER_SVC_URL") or os.getenv("DB_API", "http://localhost:8002")
USER_API_PREFIX = "/api/v1"
INTERNAL_HDR = {"X-Internal-Request": "true"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = decode_access_token(token)
    sub = payload.get("sub")
    if not isinstance(sub, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_id = UUID(sub)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{USER_API_PREFIX}/users/{user_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)

    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Usuario no existe")

    user_data = resp.json()

    # Normalize user state from user service
    user_state = user_data.get("state")
    if user_state in ("UserState.ACTIVE", "Active"):
        user_data["state"] = "A"

    if user_data.get("state") != "A":
        raise HTTPException(status_code=400, detail="Usuario inactivo o bloqueado")

    return User(**user_data)


def role_checker(allowed: list[str]):
    async def _checker(user: User = Depends(get_current_user)):
        if user.role is None or user.role.name not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Permiso denegado"
            )
        return user

    return _checker
