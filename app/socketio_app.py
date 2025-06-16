from datetime import datetime
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.servicios.socket import sio

app = FastAPI(
    title="Backend SmartPay (Socket.IO)",
    description="Servicio FastAPI con soporte Socket.IO para mensajería en tiempo real.",
    version="2.0.0",
)


# Mapeo de sid -> device_id para estadísticas rápidas
connected_devices: Dict[str, str] = {}


class MessageRequest(BaseModel):
    """Modelo de entrada para enviar un mensaje a una sala/dispositivo."""

    message: str
    sender_id: Optional[str] = None
    room_id: str  # dispositivo/sala destino obligatorio


# --------------------
# Socket.IO eventos
# --------------------


@sio.on("joinRoom")
async def handle_join_room(sid, data):
    """Cliente solicita unirse a su sala usando su *deviceId*.

    Expects: { "deviceId": "abc123" }
    """
    print("\n=== HANDLE_JOIN_ROOM INICIO ===")
    print(f"[JOIN_ROOM] SID: {sid}")
    print(f"[JOIN_ROOM] Data recibida: {data}")
    print(f"[JOIN_ROOM] Tipo de data: {type(data)}")

    device_id = data.get("deviceId") if isinstance(data, dict) else None
    if not device_id:
        print("[JOIN_ROOM] Error: deviceId faltante")
        await sio.emit("error", {"error": "deviceId missing"}, room=sid)
        return

    print(f"[JOIN_ROOM] Uniendo dispositivo {device_id} (SID: {sid}) a la sala...")

    try:
        # registrar en la sala cuyo nombre es el mismo device_id
        await sio.enter_room(sid, device_id, "/")
        connected_devices[sid] = device_id
        print(f"[JOIN_ROOM] Dispositivo {device_id} unido a la sala correctamente")

        # Mensaje de confirmación individual
        confirmation_data = {
            "message": f"Device {device_id} joined room successfully",
            "device_id": device_id,
            "connected_devices": len(set(connected_devices.values())),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        print(
            f"[JOIN_ROOM] Enviando confirmación a SID {sid} con datos: {confirmation_data}"
        )

        await sio.emit(
            "connection",
            confirmation_data,
            room=sid,
        )

        print("[JOIN_ROOM] Confirmación enviada exitosamente")

    except Exception as e:
        print(f"[JOIN_ROOM] Error al unir a la sala: {str(e)}")
        import traceback

        traceback.print_exc()
        await sio.emit("error", {"error": f"Error joining room: {str(e)}"}, room=sid)

    print("=== HANDLE_JOIN_ROOM FIN ===\n")


@sio.on("disconnect")
async def handle_disconnect(sid):
    """Limpia registro cuando un cliente se desconecta."""
    connected_devices.pop(sid, None)


# --------------------
# Endpoints HTTP
# --------------------


@app.get("/", tags=["Health"])
def health_check():
    """Health-check básico."""

    return {
        "status": "healthy",
        "service": "Backend SmartPay (Socket.IO)",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "connected_devices": len(set(connected_devices.values())),
    }


@app.post("/broadcast", tags=["Messaging"])
async def broadcast_message(req: MessageRequest):
    """Envía un mensaje a la sala/dispositivo indicado por *room_id*."""

    if not connected_devices:
        raise HTTPException(status_code=404, detail="No devices connected")

    target_room = req.room_id
    if target_room not in connected_devices.values():
        raise HTTPException(status_code=404, detail="Target device not connected")

    payload = {
        "type": "broadcast",
        "message": req.message,
        "from_device": req.sender_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    await sio.emit("broadcast", payload, room=target_room)
    return {"status": "success", "recipients": 1, **payload}


@app.get("/connections", tags=["Monitoring"])
def get_connections():
    """Devuelve información sobre conexiones activas."""

    return {
        "connected_devices": len(set(connected_devices.values())),
        "rooms": list(set(connected_devices.values())),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
