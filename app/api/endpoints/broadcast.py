from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.servicios.socket import message

router = APIRouter()


class MessageRequest(BaseModel):
    """Modelo de entrada para envío de mensajes."""

    message: str
    sender_id: Optional[str] = None
    room_id: str
    device_id: Optional[str] = None


@router.post("/broadcast")
async def broadcast_message(message_request: MessageRequest):
    """
    Envía un mensaje a todos los dispositivos conectados o a una sala específica.

    Parámetros:
    - message: El mensaje a enviar
    - sender_id: (opcional) ID del remitente
    - room_id: ID de la sala/dispositivo destino (usar 'broadcast' para todos)
    - device_id: (opcional) ID del dispositivo específico
    """
    try:
        print("\n=== SOLICITUD DE BROADCAST ===")
        print(f"[BROADCAST] Mensaje recibido: {message_request.dict()}")

        # Validar el mensaje
        if not message_request.message:
            raise HTTPException(
                status_code=400, detail="El mensaje no puede estar vacío"
            )

        # Preparar los datos del mensaje
        message_data = {
            "message": message_request.message,
            "timestamp": datetime.utcnow().isoformat(),
            "sender_id": message_request.sender_id or "server",
            "room_id": message_request.room_id,
        }

        # Usar la función del módulo de socket para enviar el mensaje
        result = await message(
            sid=None,  # No hay SID específico para mensajes desde la API HTTP
            data={
                **message_data,
                "target_device_id": message_request.device_id,
                "is_broadcast": message_request.room_id.lower() == "broadcast",
            },
        )

        # Si hay un error en el envío, lanzar una excepción
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        # Devolver la respuesta exitosa
        return {
            "status": "success",
            "message": "Mensaje enviado exitosamente",
            "details": {
                **message_data,
                "sent_to": result.get("sent_to", "unknown"),
                "recipient_count": result.get("recipient_count", 0),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error al enviar mensaje: {str(e)}"
        print(f"[ERROR] {error_msg}")
        import traceback

        print(f"[ERROR] Traceback: {traceback.format_exc()}")

        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": error_msg,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
