from typing import Dict, Set

import socketio

# 1. Crear una instancia del servidor Socket.IO
# El modo asíncrono 'asgi' es compatible con FastAPI.
# Se habilita CORS para permitir conexiones desde cualquier origen.
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


class ConnectionManager:
    """
    Gestiona las conexiones de Socket.IO, asociando device_id con los SIDs.
    Utiliza las salas de Socket.IO para agrupar conexiones por device_id.
    """

    def __init__(self):
        # Mapa de device_id -> set de SIDs (Session IDs) de Socket.IO
        self.active_connections: Dict[str, Set[str]] = {}

    async def connect(self, sid: str, device_id: str):
        """
        Asocia un device_id con un SID y lo une a una sala con su nombre.
        """
        # Almacena la asociación
        self.active_connections.setdefault(device_id, set()).add(sid)
        # Une el cliente a una sala con el nombre del device_id
        await sio.enter_room(sid, room=device_id)
        print(f"Device {device_id} (SID: {sid}) connected and joined room.")

    async def disconnect(self, sid: str):
        """
        Gestiona la desconexión de un cliente.
        Encuentra el device_id asociado al SID y lo elimina de la gestión.
        """
        device_to_remove = None
        for device_id, sids in self.active_connections.items():
            if sid in sids:
                sids.discard(sid)
                if not sids:  # Si no quedan más conexiones para este dispositivo
                    device_to_remove = device_id
                break

        if device_to_remove:
            self.active_connections.pop(device_to_remove)
            print(f"Device {device_to_remove} fully disconnected.")

        print(f"Client with SID {sid} disconnected.")

    async def send_to_device(self, device_id: str, event: str, data: dict):
        """
        Envía un evento con datos a un device_id específico usando su sala.
        """
        if device_id in self.active_connections:
            await sio.emit(event, data, room=device_id)
            print(f"Sent event '{event}' to device {device_id}")

    async def broadcast(self, event: str, data: dict):
        """
        Envía un evento a todos los clientes conectados.
        """
        await sio.emit(event, data)
        print(f"Broadcasted event '{event}' to all clients.")

    def total_devices(self) -> int:
        """Número de dispositivos únicos conectados."""
        return len(self.active_connections)


# Crear una instancia global del manager
manager = ConnectionManager()


# Definir los manejadores de eventos de Socket.IO
@sio.event
async def connect(sid, environ):
    """
    Evento que se dispara cuando un cliente se conecta.
    'environ' contiene la información de la petición HTTP.
    """
    print(f"Client connected: {sid}")
    # El cliente debe enviar un evento 'joinRoom' para identificarse.
    await sio.emit("connection_ready", {"sid": sid}, to=sid)


@sio.event
async def joinRoom(sid, data):
    """
    Evento personalizado para que el cliente se una a una sala (se identifique).
    El cliente debe enviar: {'deviceId': '...'}
    """
    device_id = data.get("deviceId")
    if not device_id:
        print(f"joinRoom failed for SID {sid}: 'deviceId' not provided.")
        await sio.emit("error", {"message": "'deviceId' is required"}, to=sid)
        return

    await manager.connect(sid, device_id)
    welcome_msg = {
        "type": "connection_success",
        "message": f"Device {device_id} connected successfully.",
        "connected_devices": manager.total_devices(),
    }
    await sio.emit("message", welcome_msg, to=sid)


@sio.event
async def disconnect(sid):
    """
    Evento que se dispara cuando un cliente se desconecta.
    """
    await manager.disconnect(sid)


@sio.on("*")
async def catch_all(event, sid, data):
    """
    Manejador para cualquier otro evento no definido. Útil para depuración.
    """
    print(f"Received event '{event}' from {sid} with data: {data}")
