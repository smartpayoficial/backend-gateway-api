from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_socketio import SocketManager
from pydantic import BaseModel

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="Socket.IO API",
    description="A FastAPI service with Socket.IO",
    version="1.0.0",
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar Socket.IO
socket_manager = SocketManager(
    app=app,
    mount_location="/socket.io",
    cors_allowed_origins=[],
    async_mode="asgi",
    engineio_logger=True,
)

# Mapa para mantener el seguimiento de las conexiones
active_connections: Dict[str, List[str]] = {}


class MessageRequest(BaseModel):
    """Modelo de entrada para envío de mensajes."""

    message: str
    sender_id: Optional[str] = None
    room_id: str


# Eventos de Socket.IO
@socket_manager.on("connect")
async def handle_connect(sid, environ, auth):
    """Maneja la conexión de un nuevo cliente."""
    try:
        # Obtener el device_id del query string
        query = environ.get("QUERY_STRING", "")
        query_params = dict(qc.split("=") for qc in query.split("&") if "=" in qc)
        device_id = query_params.get("device_id")

        if not device_id:
            print("Conexión rechazada: No se proporcionó device_id")
            return False

        # Registrar la conexión
        if device_id not in active_connections:
            active_connections[device_id] = []

        if sid not in active_connections[device_id]:
            active_connections[device_id].append(sid)

        print(f"Cliente conectado: {sid} (device_id: {device_id})")

        # Enviar mensaje de bienvenida
        await socket_manager.emit(
            "message",
            {
                "type": "connection",
                "message": f"Device {device_id} connected",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "device_id": device_id,
                "sid": sid,
            },
            room=sid,
        )

        return True

    except Exception as e:
        print(f"Error en handle_connect: {str(e)}")
        return False


@socket_manager.on("disconnect")
async def handle_disconnect(sid):
    """Maneja la desconexión de un cliente."""
    try:
        # Encontrar y eliminar el SID de todas las conexiones
        for device_id, sids in list(active_connections.items()):
            if sid in sids:
                sids.remove(sid)
                print(f"Cliente desconectado: {sid} (device_id: {device_id})")

            # Eliminar el device_id si no hay más conexiones
            if not sids:
                active_connections.pop(device_id, None)
    except Exception as e:
        print(f"Error en handle_disconnect: {str(e)}")


@socket_manager.on("message")
async def handle_message(sid, data):
    """Maneja los mensajes entrantes de los clientes."""
    try:
        print(f"Mensaje recibido de {sid}: {data}")

        # Enviar el mensaje de vuelta al remitente
        await socket_manager.emit(
            "message",
            {
                "type": "echo",
                "message": data,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "sid": sid,
            },
            room=sid,
        )
    except Exception as e:
        print(f"Error en handle_message: {str(e)}")


# Endpoints HTTP
@app.get("/")
async def root():
    """Endpoint raíz."""
    return {
        "service": "Socket.IO API",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "connected_devices": len(active_connections),
        "total_connections": sum(len(sids) for sids in active_connections.values()),
    }


@app.get("/connections")
async def get_connections():
    """Obtiene información sobre las conexiones actuales."""
    return {
        "connected_devices": len(active_connections),
        "total_connections": sum(len(sids) for sids in active_connections.values()),
        "devices": [
            {"id": k, "connections": len(v)} for k, v in active_connections.items()
        ],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/broadcast")
async def broadcast_message(message_request: MessageRequest):
    """Envía un mensaje a todos los dispositivos conectados."""
    try:
        message = {
            "type": "broadcast",
            "message": message_request.message,
            "sender_id": message_request.sender_id or "server",
            "room_id": message_request.room_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Contar destinatarios
        recipients = sum(len(sids) for sids in active_connections.values())

        # Enviar a todos los clientes
        await socket_manager.emit("message", message)

        return {
            "status": "message_sent",
            "message": "Mensaje enviado a todos los clientes conectados",
            "recipients": recipients,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
