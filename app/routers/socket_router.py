from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Importar el manager y la función de servicio refactorizada
from app.services.socket_service import manager, send_and_log_action

router = APIRouter()


class MessageRequest(BaseModel):
    message: str
    sender_id: Optional[str] = None
    room_id: str  # obligatorio


class ActionBody(BaseModel):
    applied_by_id: UUID
    payload: Optional[Dict[str, Any]] = None


@router.post("/action/{device_id}/block_sim", tags=["Device Actions"])
async def action_block_sim(device_id: UUID, body: ActionBody):
    return await send_and_log_action(
        device_id, "BLOCK_SIM", body.applied_by_id, body.payload
    )


@router.post("/action/{device_id}/locate", tags=["Device Actions"])
async def action_locate(device_id: UUID, body: ActionBody):
    return await send_and_log_action(
        device_id, "locate", body.applied_by_id, body.payload
    )


@router.post("/action/{device_id}/refresh", tags=["Device Actions"])
async def action_refresh(device_id: UUID, body: ActionBody):
    return await send_and_log_action(
        device_id, "refresh", body.applied_by_id, body.payload
    )


@router.post("/action/{device_id}/notify", tags=["Device Actions"])
async def action_notify(device_id: UUID, body: ActionBody):
    return await send_and_log_action(
        device_id, "notify", body.applied_by_id, body.payload
    )


@router.post("/action/{device_id}/unenroll", tags=["Device Actions"])
async def action_unenroll(device_id: UUID, body: ActionBody):
    return await send_and_log_action(
        device_id, "unenroll", body.applied_by_id, body.payload
    )


@router.post("/action/{device_id}/unblock_sim", tags=["Device Actions"])
async def action_unblock_sim(device_id: UUID, body: ActionBody):
    return await send_and_log_action(
        device_id, "UNBLOCK_SIM", body.applied_by_id, body.payload
    )


@router.post("/action/{device_id}/exception", tags=["Device Actions"])
async def action_exception(device_id: UUID, body: ActionBody):
    return await send_and_log_action(
        device_id, "exception", body.applied_by_id, body.payload
    )


@router.get("/connections", tags=["Monitoring"])
def get_connections():
    """
    Get information about current WebSocket connections
    """
    return {
        "connected_devices": manager.total_devices(),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/broadcast", tags=["Messaging"])
async def broadcast_message(message_request: MessageRequest):
    """
    Envío de mensajes.
    - **message**: Contenido a enviar.
    - **sender_id**: Identificador (opcional) del emisor.
    - **room_id**: Sala/Dispositivo destino. Obligatorio.
    """
    if not manager.active_connections:
        raise HTTPException(status_code=404, detail="No devices connected")
    base_msg = {
        "type": "broadcast",
        "message": message_request.message,
        "from_device": message_request.sender_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    target = message_request.room_id
    if target not in manager.active_connections:
        raise HTTPException(status_code=404, detail="Target device not connected")

    directed_msg = {**base_msg, "recipients": 1, "room_id": target}
    # Enviar como un evento 'message' al dispositivo/sala de destino
    await manager.send_to_device(target, event="message", data=directed_msg)
    return {
        "status": "success",
        "message": "Message sent to device successfully",
        "recipients": 1,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
