from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.models.action import ActionCreate

# Importar el manager y sio desde el servicio de socket refactorizado
from app.services.socket_service import manager
from app.servicios import action as action_service

router = APIRouter()


class MessageRequest(BaseModel):
    message: str
    sender_id: Optional[str] = None
    room_id: str  # obligatorio


class ActionBody(BaseModel):
    applied_by_id: UUID
    payload: Optional[Dict[str, Any]] = None


async def send_action_command(
    device_id: str, command: str, applied_by_id: UUID, payload: Optional[dict] = None
):
    """
    Logs an action and sends it to a device if connected.
    - If the device is connected, sends the command and returns a 200 OK response.
    - If the device is offline, queues the action and returns a 202 Accepted response.
    """
    # 1. Log the action if the device_id is a valid UUID.
    try:
        # Try to convert device_id to UUID for logging purposes.
        # If it fails, it's a non-standard ID (e.g., from a web client), so we skip logging.
        device_uuid = UUID(device_id)
        action_log = ActionCreate(
            device_id=device_uuid,
            applied_by_id=applied_by_id,
            action=command,
            description=f"Action '{command}' queued for device {device_id}. Payload: {payload or '{}'}",
        )
        await action_service.create_action(action_log)
    except (ValueError, Exception) as e:
        # ValueError for failed UUID conversion, Exception for DB errors.
        # We don't raise an exception, as sending the command is more critical.
        print(f"INFO: Could not log action for device '{device_id}'. Reason: {e}")

    timestamp = datetime.utcnow().isoformat() + "Z"
    device_id_str = str(device_id)

    # 2. Check connection and attempt to send the command.
    if device_id_str not in manager.active_connections:
        # Device is offline, return 202 Accepted
        response_data = {
            "status": "Pending",
            "detail": "Device is offline. Action has been queued for later execution.",
            "command": command,
            "device_id": device_id_str,
            "timestamp": timestamp,
        }
        return JSONResponse(status_code=202, content=response_data)

    # Device is online, send the command via Socket.IO
    action_msg = {
        "command": command,
        "device_id": device_id_str,
        "payload": payload or {},
        "timestamp": timestamp,
    }
    # El nombre del evento es 'action', los datos son el diccionario action_msg
    await manager.send_to_device(device_id_str, event="action", data=action_msg)

    response_data = {
        "status": "sent",
        "detail": "Action sent to online device successfully.",
        "command": command,
        "device_id": device_id_str,
        "timestamp": timestamp,
    }
    return JSONResponse(status_code=200, content=response_data)


@router.post("/action/{device_id}/block", tags=["Device Actions"])
async def action_block(device_id: str, body: ActionBody):
    return await send_action_command(
        device_id, "block", body.applied_by_id, body.payload
    )


@router.post("/action/{device_id}/locate", tags=["Device Actions"])
async def action_locate(device_id: str, body: ActionBody):
    return await send_action_command(
        device_id, "locate", body.applied_by_id, body.payload
    )


@router.post("/action/{device_id}/refresh", tags=["Device Actions"])
async def action_refresh(device_id: str, body: ActionBody):
    return await send_action_command(
        device_id, "refresh", body.applied_by_id, body.payload
    )


@router.post("/action/{device_id}/notify", tags=["Device Actions"])
async def action_notify(device_id: str, body: ActionBody):
    return await send_action_command(
        device_id, "notify", body.applied_by_id, body.payload
    )


@router.post("/action/{device_id}/unenroll", tags=["Device Actions"])
async def action_unenroll(device_id: str, body: ActionBody):
    return await send_action_command(
        device_id, "unenroll", body.applied_by_id, body.payload
    )


@router.post("/action/{device_id}/unblock", tags=["Device Actions"])
async def action_unblock(device_id: str, body: ActionBody):
    return await send_action_command(
        device_id, "unblock", body.applied_by_id, body.payload
    )


@router.post("/action/{device_id}/exception", tags=["Device Actions"])
async def action_exception(device_id: str, body: ActionBody):
    return await send_action_command(
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
