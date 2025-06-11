"""
Endpoints para el envío de comandos a dispositivos.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.servicios.socket import command_manager

router = APIRouter()


# Modelos de solicitud
class UnBlockDeviceRequest(BaseModel):
    reason: str = Field("", description="Razón del desbloqueo")
    duration: int = Field(3600, description="Duración del desbloqueo en segundos")


class LocateDeviceRequest(BaseModel):
    timeout: int = Field(30, description="Tiempo máximo de espera en segundos")


class RefreshDeviceRequest(BaseModel):
    force: bool = Field(False, description="Forzar actualización")


class NotificationRequest(BaseModel):
    title: str = Field(..., description="Título de la notificación")
    message: str = Field(..., description="Mensaje de la notificación")
    priority: str = Field("normal", description="Prioridad (low, normal, high)")


class UnenrollDeviceRequest(BaseModel):
    reason: str = Field("", description="Razón de la baja")


class ExceptionRequest(BaseModel):
    error_code: str = Field(..., description="Código de error")
    error_message: str = Field(..., description="Mensaje de error")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales")


# Endpoints
@router.post("/{device_id}/block", summary="Bloquear dispositivo")
async def block_device(device_id: str):
    """Bloquea un dispositivo por un tiempo determinado."""
    result = await command_manager.block_device(
        device_id=device_id
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/{device_id}/unblock", summary="Desbloquear dispositivo")
async def unblock_device(device_id: str, request: UnBlockDeviceRequest):
    """Desbloquea un dispositivo previamente bloqueado."""
    result = await command_manager.unblock_device(device_id= device_id, reason=request.reason, duration=request.duration)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/{device_id}/locate", summary="Localizar dispositivo")
async def locate_device(device_id: str, request: LocateDeviceRequest):
    """Solicita la ubicación actual de un dispositivo."""
    result = await command_manager.locate_device(
        device_id=device_id, timeout=request.timeout
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/{device_id}/refresh", summary="Actualizar estado")
async def refresh_device(device_id: str, request: RefreshDeviceRequest):
    """Solicita una actualización de estado del dispositivo."""
    result = await command_manager.refresh_device(
        device_id=device_id, force=request.force
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/{device_id}/notify", summary="Enviar notificación")
async def send_notification(device_id: str, request: NotificationRequest):
    """Envía una notificación al dispositivo."""
    result = await command_manager.send_notification(
        device_id=device_id,
        title=request.title,
        message=request.message,
        priority=request.priority,
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/{device_id}/unenroll", summary="Dar de baja dispositivo")
async def unenroll_device(device_id: str, request: UnenrollDeviceRequest):
    """Da de baja un dispositivo del sistema."""
    result = await command_manager.unenroll_device(
        device_id=device_id, reason=request.reason
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/{device_id}/exception", summary="Reportar excepción")
async def report_exception(device_id: str, request: ExceptionRequest):
    """Reporta una excepción al dispositivo."""
    result = await command_manager.report_exception(
        device_id=device_id,
        error_code=request.error_code,
        error_message=request.error_message,
        details=request.details,
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result
