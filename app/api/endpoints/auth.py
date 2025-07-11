import os
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field

from app.auth.security import (
    create_access_token,
    decode_access_token,
    generate_password_reset_token,
    get_password_hash,
    verify_password,
    verify_password_reset_token,
)
from app.services.email import send_password_reset_email

router = APIRouter()


class RefreshTokenIn(BaseModel):
    refresh_token: str


class PasswordResetRequestIn(BaseModel):
    dni: str = Field(
        ..., description="DNI del usuario que solicita restablecer su contraseña"
    )


class PasswordResetRequestOut(BaseModel):
    message: str


class PasswordResetIn(BaseModel):
    token: str = Field(..., description="Token de restablecimiento de contraseña")
    new_password: str = Field(..., min_length=8, description="Nueva contraseña")


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


@router.post("/login", response_model=TokenOut)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint seguro de login. Solo requiere username y password (vía formulario).
    No acepta ni expone ningún otro dato sensible.
    """
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{USER_API_PREFIX}/users/by-username/{form_data.username}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    user = resp.json()
    is_active = user.get("is_active")
    if is_active is None:
        is_active = str(user.get("state", "")).lower() == "active"

    password_valid = verify_password(form_data.password, user["password_hash"])

    if not is_active or not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas"
        )

    token_data = {
        "sub": user["user_id"],
        "username": user["username"],
        "role": (
            user["role"]["name"]
            if isinstance(user.get("role"), dict)
            else user.get("role", "")
        ),
    }
    token = create_access_token(token_data)
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


@router.post("/password-reset/request", response_model=PasswordResetRequestOut)
async def request_password_reset(request: Request, data: PasswordResetRequestIn):
    """Solicita un restablecimiento de contraseña proporcionando el DNI del usuario.

    Se enviará un correo electrónico con un enlace para restablecer la contraseña
    si el DNI corresponde a un usuario registrado.
    """
    # Buscar usuario por DNI
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{USER_API_PREFIX}/users/by-dni/{data.dni}"
        resp = await client.get(url, headers=INTERNAL_HDR)

    # Siempre devolver un mensaje genérico para evitar enumerar usuarios
    if resp.status_code != 200:
        return {
            "message": "Si el DNI está registrado, recibirás un correo con instrucciones."
        }

    user = resp.json()
    email = user.get("email")

    if not email:
        return {
            "message": "Si el DNI está registrado, recibirás un correo con instrucciones."
        }

    # Generar token para restablecer contraseña
    token = generate_password_reset_token(email)

    # Construir URL de restablecimiento
    base_url = os.getenv("RESET_PASSWORD_BASE_URL", str(request.base_url))
    reset_url = f"{base_url}/reset-password?token={token}"

    # Mostrar el enlace de restablecimiento directamente en la consola
    print("\n" + "=" * 80)
    print("ENLACE DE RESTABLECIMIENTO DE CONTRASEÑA GENERADO EN EL ENDPOINT:")
    print(f"URL: {reset_url}")
    print(f"Para: {email}")
    print("=" * 80 + "\n")

    # Enviar correo electrónico
    await send_password_reset_email(email, reset_url)

    return {
        "message": "Si el DNI está registrado, recibirás un correo con instrucciones."
    }


@router.post("/password-reset/confirm", response_model=PasswordResetRequestOut)
async def confirm_password_reset(data: PasswordResetIn):
    """Confirma el restablecimiento de contraseña utilizando el token enviado por correo.

    Verifica el token y actualiza la contraseña del usuario si el token es válido.
    """
    try:
        # Verificar token y obtener email
        email = verify_password_reset_token(data.token)

        # Buscar usuario por email
        async with httpx.AsyncClient() as client:
            url = f"{USER_SVC_URL}{USER_API_PREFIX}/users/by-email/{email}"
            resp = await client.get(url, headers=INTERNAL_HDR)

        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )

        user = resp.json()
        user_id = user.get("user_id")

        # Actualizar contraseña en el servicio de usuarios
        async with httpx.AsyncClient() as client:
            update_url = f"{USER_SVC_URL}{USER_API_PREFIX}/users/{user_id}"
            update_resp = await client.patch(
                update_url, json={"password": data.new_password}, headers=INTERNAL_HDR
            )

            if update_resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error al actualizar la contraseña",
                )

        return {"message": "Contraseña actualizada correctamente"}

    except HTTPException as e:
        # Re-lanzar excepciones HTTP ya formateadas
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al procesar la solicitud: {str(e)}",
        )
