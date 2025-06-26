import json
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.services.socket_service import ConnectionManager

router = APIRouter()
manager = ConnectionManager()


class MessageRequest(BaseModel):
    message: str
    sender_id: Optional[str] = None
    room_id: str  # obligatorio


class ActionPayload(BaseModel):
    payload: Optional[Dict[str, Any]] = None


async def send_action_command(
    device_id: str, command: str, payload: Optional[dict] = None
):
    if device_id not in manager.active_connections:
        raise HTTPException(status_code=404, detail="Target device not connected")
    action_msg = {
        "event": "action",
        "command": command,
        "device_id": device_id,
        "payload": payload or {},
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    await manager.send_to_device(device_id, json.dumps(action_msg))
    return {
        "status": "sent",
        "command": command,
        "device_id": device_id,
        "timestamp": action_msg["timestamp"],
    }


@router.post("/action/block", tags=["Device Actions"])
async def action_block(device_id: str, body: Optional[ActionPayload] = None):
    return await send_action_command(device_id, "block", body.payload if body else None)


@router.post("/action/locate", tags=["Device Actions"])
async def action_locate(device_id: str, body: Optional[ActionPayload] = None):
    return await send_action_command(
        device_id, "locate", body.payload if body else None
    )


@router.post("/action/refresh", tags=["Device Actions"])
async def action_refresh(device_id: str, body: Optional[ActionPayload] = None):
    return await send_action_command(
        device_id, "refresh", body.payload if body else None
    )


@router.post("/action/notify", tags=["Device Actions"])
async def action_notify(device_id: str, body: Optional[ActionPayload] = None):
    return await send_action_command(
        device_id, "notify", body.payload if body else None
    )


@router.post("/action/unenroll", tags=["Device Actions"])
async def action_unenroll(device_id: str, body: Optional[ActionPayload] = None):
    return await send_action_command(
        device_id, "unenroll", body.payload if body else None
    )


@router.post("/action/unblock", tags=["Device Actions"])
async def action_unblock(device_id: str, body: Optional[ActionPayload] = None):
    return await send_action_command(
        device_id, "unblock", body.payload if body else None
    )


@router.post("/action/exception", tags=["Device Actions"])
async def action_exception(device_id: str, body: Optional[ActionPayload] = None):
    return await send_action_command(
        device_id, "exception", body.payload if body else None
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
    await manager.send_to_device(target, json.dumps(directed_msg))
    return {
        "status": "success",
        "message": "Message sent to device successfully",
        "recipients": 1,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.websocket("/ws")
async def websocket_generic(websocket: WebSocket):
    """
    WebSocket generico. El cliente debe enviar un JSON con:
    {"deviceId": "...", "event": "joinRoom"}
    para quedar registrado en el manager.
    """
    await websocket.accept()
    device_id: Optional[str] = None
    try:
        join_payload = await websocket.receive_text()
        try:
            join_data = json.loads(join_payload)
        except json.JSONDecodeError:
            await websocket.send_text(
                json.dumps({"error": "Invalid JSON for joinRoom"})
            )
            await websocket.close()
            return
        if join_data.get("event") != "joinRoom" or "deviceId" not in join_data:
            await websocket.send_text(
                json.dumps({"error": "First message must be joinRoom with deviceId"})
            )
            await websocket.close()
            return
        device_id = join_data["deviceId"]
        await manager.connect(device_id, websocket)
        welcome_msg = {
            "type": "connection",
            "message": f"Device {device_id} connected successfully",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "connected_devices": manager.total_devices(),
        }
        await manager.send_to_device(device_id, json.dumps(welcome_msg))
        while True:
            data_text = await websocket.receive_text()
            response = {
                "type": "echo",
                "device_id": device_id,
                "original_message": data_text,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            await manager.send_to_device(device_id, json.dumps(response))
    except WebSocketDisconnect:
        if device_id:
            manager.disconnect(device_id, websocket)
            print(f"Device {device_id} disconnected")
