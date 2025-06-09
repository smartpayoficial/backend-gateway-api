import json
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class ConnectionManager:
    """Gestiona conexiones WebSocket identificadas por **device_id**."""

    def __init__(self):
        # Mapa device_id -> set de WebSockets activos
        self.active_connections: dict[str, set[WebSocket]] = {}

    async def connect(self, device_id: str, websocket: WebSocket):
        """Acepta la conexión y la registra por *device_id*."""
        self.active_connections.setdefault(device_id, set()).add(websocket)

    def disconnect(self, device_id: str, websocket: WebSocket):
        """Elimina el *websocket* del dispositivo; si no quedan sockets se borra la clave."""
        if device_id in self.active_connections:
            self.active_connections[device_id].discard(websocket)
            if not self.active_connections[device_id]:
                self.active_connections.pop(device_id)

    async def send_to_device(self, device_id: str, message: str):
        """Envía mensaje a un dispositivo concreto si está conectado."""
        sockets = self.active_connections.get(device_id)
        if sockets:
            for ws in list(sockets):
                try:
                    await ws.send_text(message)
                except Exception:
                    # Remove faulty socket
                    self.disconnect(device_id, ws)

    async def broadcast(self, message: str):
        """Envía mensaje a todos los dispositivos conectados."""
        disconnected: List[tuple[str, WebSocket]] = []
        for dev_id, sockets in self.active_connections.items():
            for conn in list(sockets):
                try:
                    await conn.send_text(message)
                except Exception:
                    disconnected.append((dev_id, conn))

        for dev_id, sock in disconnected:
            self.disconnect(dev_id, sock)

    def total_devices(self) -> int:
        """Número de dispositivos únicos conectados."""
        return len(self.active_connections)


class MessageRequest(BaseModel):
    """Modelo de entrada para envío a **un** dispositivo/sala.

    - **message**: Texto a enviar.
    - **sender_id**: Identificador del emisor (opcional).
    - **room_id**: Sala/Dispositivo destino (obligatorio).
    """

    message: str
    sender_id: Optional[str] = None
    room_id: str  # obligatorio


app = FastAPI(
    title="Simple API",
    description="A simple FastAPI service with WebSockets",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ConnectionManager()


@app.get("/", tags=["Health"])
def health_check():
    """
    Health check endpoint

    Returns the service status and current timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "Simple API",
        "version": "1.0.0",
        "connected_devices": manager.total_devices(),
    }


@app.websocket("/ws/{device_id}")
async def websocket_generic(websocket: WebSocket, device_id: str) -> None:
    """WebSocket endpoint.

    Args:
        websocket: The WebSocket connection instance
        device_id: The ID of the device connecting
    """
    # Aceptar la conexión WebSocket sin headers personalizados
    # Los headers CORS se manejan a nivel de la aplicación FastAPI
    await websocket.accept()

    try:
        # Register the connection
        await manager.connect(device_id, websocket)

        # Send welcome message
        welcome_msg = {
            "type": "connection",
            "message": f"Device {device_id} connected successfully",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "connected_devices": manager.total_devices(),
        }
        await manager.send_to_device(device_id, json.dumps(welcome_msg))
        print(f"Device {device_id} connected successfully")

        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                print(f"Received from {device_id}: {data}")
                try:
                    message = json.loads(data)
                    response = {
                        "type": "echo",
                        "device_id": device_id,
                        "message": message,
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                    }
                except json.JSONDecodeError:
                    response = {
                        "type": "echo",
                        "device_id": device_id,
                        "message": data,
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                    }
                await websocket.send_text(json.dumps(response))
                print(f"Sent to {device_id}: {response}")

            except json.JSONDecodeError:
                error_msg = {
                    "type": "error",
                    "message": "Invalid JSON received",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
                await websocket.send_text(json.dumps(error_msg))
                print(f"JSON error for {device_id}")

    except WebSocketDisconnect:
        print(f"Device {device_id} disconnected")
        manager.disconnect(device_id, websocket)
    except Exception as e:
        print(f"WebSocket error for {device_id}: {str(e)}")
        try:
            await websocket.close()
        except (RuntimeError, ConnectionError, WebSocketDisconnect) as e:
            print(f"Error closing WebSocket: {e}")
        manager.disconnect(device_id, websocket)
        print(f"Connection closed for {device_id}")


@app.post("/broadcast", tags=["Messaging"])
async def broadcast_message(message_request: MessageRequest):
    """Envío de mensajes.

    - **message**: Contenido a enviar.
    - **sender_id**: Identificador (opcional) del emisor.
    - **room_id**: Sala/Dispositivo destino. Si no se especifica, se envía a todos los dispositivos.
    """

    if not manager.active_connections:
        raise HTTPException(status_code=404, detail="No devices connected")

    # Mensaje base
    base_msg = {
        "type": "broadcast",
        "message": message_request.message,
        "from_device": message_request.sender_id or "server",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    # Si no hay room_id, enviar a todos los dispositivos
    if not message_request.room_id:
        broadcast_msg = {
            **base_msg,
            "recipients": len(manager.active_connections),
            "broadcast": True,
        }
        await manager.broadcast(json.dumps(broadcast_msg))
        return {
            "status": "success",
            "message": "Broadcast message sent to all devices",
            "recipients": len(manager.active_connections),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    # Envío dirigido a un solo dispositivo
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


@app.get("/connections", tags=["Monitoring"])
def get_connections():
    """
    Get information about current WebSocket connections
    """
    return {
        "connected_devices": manager.total_devices(),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
