from datetime import datetime
from typing import Dict, Optional, Set
from uuid import UUID

import socketio
from fastapi.responses import JSONResponse

from app.models.action import ActionCreate, ActionState, ActionUpdate
from app.services import action as action_service

# 1. Crear una instancia del servidor Socket.IO
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


# --- Application-Level Service Functions ---


async def send_and_log_action(
    device_id: UUID, command: str, applied_by_id: UUID, payload: Optional[dict] = None
):
    """
    Logs an action and sends it to a device if connected.
    - If the device is connected, sends the command and returns a 200 OK response.
    - If the device is offline, queues the action and returns a 202 Accepted response.
    """
    created_action = None
    # 1. Create the action record.
    try:
        # Mapear comandos específicos a tipos de acción genéricos para el registro en la BD.
        # El servicio de BD puede tener un conjunto de acciones más limitado que el gateway.
        db_action_map = {
            "block_sim": "block",
            "unblock_sim": "unblock",
        }
        db_action_command = db_action_map.get(command, command)

        action_log = ActionCreate(
            device_id=device_id,
            applied_by_id=applied_by_id,
            action=db_action_command,  # Usar el comando mapeado para el registro en la BD
            description=f"Action '{command}' initiated for device {device_id}.",  # Mantener el comando original en la descripción
        )
        created_action = await action_service.create_action(action_log)
    except Exception as e:
        # Handle potential errors during action creation (e.g., DB connection).
        print(f"ERROR: Could not create action for device '{device_id}'. Reason: {e}")

    timestamp = datetime.utcnow().isoformat() + "Z"
    device_id_str = str(device_id)

    # 2. Check connection and attempt to send the command.
    if device_id_str not in manager.active_connections:
        response_data = {
            "status": "Pending",
            "detail": "Device is offline. Action has been queued for later execution.",
            "command": command,
            "device_id": device_id_str,
            "timestamp": timestamp,
        }
        return JSONResponse(status_code=202, content=response_data)

    # 3. Device is online: send the command and update the action to 'applied'.
    action_msg = {
        "command": command,
        "device_id": device_id_str,
        "payload": payload or {},
        "timestamp": timestamp,
    }
    await manager.send_to_device(device_id_str, event="action", data=action_msg)

    if created_action:
        try:
            update_payload = ActionUpdate(
                state=ActionState.APPLIED,
                description=f"Action '{command}' applied to online device {device_id}.",
            )
            await action_service.update_action(created_action.action_id, update_payload)
        except Exception as e:
            print(
                f"ERROR: Could not update action {created_action.action_id} to 'applied'. Reason: {e}"
            )

    response_data = {
        "status": "sent",
        "detail": "Action sent to online device successfully.",
        "command": command,
        "device_id": device_id_str,
        "timestamp": timestamp,
    }
    return JSONResponse(status_code=200, content=response_data)


# --- Event Handlers ---


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
