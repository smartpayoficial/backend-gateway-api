import os

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.models import UserOut
from app.auth.security import decode_access_token

USER_SVC_URL = os.getenv("USER_SVC_URL") or os.getenv("DB_API", "http://localhost:8002")
USER_API_PREFIX = "/api/v1"
INTERNAL_HDR = {"X-Internal-Request": "true"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserOut:
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
    user = UserOut(
        user_id=data["user_id"],
        username=data["username"],
        is_active=data["is_active"],
        role=data["role"]["name"],
    )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    return user


def role_checker(allowed: list[str]):
    async def _checker(user: UserOut = Depends(get_current_user)):
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Permiso denegado"
            )
        return user

    return _checker
