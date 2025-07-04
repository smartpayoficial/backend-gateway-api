from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Importar el manager de la función de servicio
from app.services.socket_service import manager

router = APIRouter()


class MessageRequest(BaseModel):
    message: str
    sender_id: Optional[str] = None
    room_id: str  # obligatorio


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
