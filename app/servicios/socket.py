"""
Módulo para manejar la lógica de WebSockets con Socket.IO.
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional, Set

import socketio

# Mapa para mantener el seguimiento de las conexiones
active_connections: Dict[str, Set[str]] = {}

# Instancia de Socket.IO
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True,
    ping_timeout=60,  # Tiempo de espera para respuesta PONG (ms)
    ping_interval=25,  # Intervalo entre PINGs (segundos)
    max_http_buffer_size=1e6,
    async_handlers=True,
    allow_upgrades=True,
    http_compression=False,
    compression_threshold=0,
    cookie=None,
    cors_credentials=True,
    namespaces=["/"],
    always_connect=False,
    reconnection=True,
    reconnection_attempts=3,
    reconnection_delay=1,
    reconnection_delay_max=5,
    randomization_factor=0.5,
    websocket_extra_headers={"Access-Control-Allow-Origin": "*"},
    cors_allowed_headers=["*"],
    binary=False,
    request_timeout=60,
    manage_http_sessions=False,
)


def print_connections():
    """Imprime el estado actual de las conexiones."""
    print("\n=== ESTADO DE CONEXIONES ===")
    for device_id, sids in active_connections.items():
        print(f"Device {device_id} tiene {len(sids)} conexiones")
    print("===========================\n")


@sio.event
async def connect(sid, environ, auth):
    """Maneja nuevas conexiones de clientes."""
    try:
        print("\n" + "=" * 50)
        print("=== NUEVA CONEXIÓN DETECTADA ===")
        print(f"[CONEXIÓN] SID: {sid}")
        print(f"[CONEXIÓN] Time: {datetime.utcnow().isoformat()}")
        print(f"[CONEXIÓN] Remote IP: {environ.get('REMOTE_ADDR', 'unknown')}")
        print(f"[CONEXIÓN] Auth: {auth}")

        # Obtener device_id de los parámetros de consulta o de los headers
        query_string = environ.get("QUERY_STRING", "")
        print(f"[CONEXIÓN] Query string: {query_string}")

        # Parsear los parámetros de consulta manualmente
        params = {}
        if query_string:
            pairs = query_string.split("&")
            for pair in pairs:
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    params[key] = value

        # Obtener device_id de los parámetros o de los headers
        device_id = params.get("device_id", "unknown")

        # Si no está en los parámetros, intentar obtenerlo de los headers
        if device_id == "unknown":
            headers = {
                k.upper().replace("-", "_"): v
                for k, v in environ.items()
                if k.startswith("HTTP_")
            }
            print(f"[CONEXIÓN] Available headers: {headers}")
            device_id = headers.get("HTTP_DEVICE_ID", "unknown")

        # Si aún no se encontró device_id, usar el SID como último recurso
        if device_id == "unknown":
            device_id = f"device_{sid}"
            print(f"[CONEXIÓN] Usando SID como device_id: {device_id}")

        print(f"[CONEXIÓN] Device ID final: {device_id}")

        # Asegurarse de que el SID no esté ya registrado
        for existing_device_id, sids in list(active_connections.items()):
            if sid in sids:
                print(
                    f"[CONEXIÓN] Eliminando SID duplicado: {sid} del dispositivo {existing_device_id}"
                )
                sids.remove(sid)
                if not sids:  # Si no quedan más conexiones para este dispositivo
                    print(
                        f"[CONEXIÓN] No hay más conexiones para el dispositivo {existing_device_id}, eliminando..."
                    )
                    del active_connections[existing_device_id]

        # Agregar la nueva conexión
        if device_id not in active_connections:
            print(
                f"[CONEXIÓN] Creando nuevo conjunto de conexiones para el dispositivo: {device_id}"
            )
            active_connections[device_id] = set()

        print(f"[CONEXIÓN] Agregando SID {sid} al dispositivo {device_id}")
        active_connections[device_id].add(sid)
        print(f"[CONEXIÓN] Estado DESPUÉS de registrar conexión: {active_connections}")
        print_connections()

        # Crear datos de confirmación
        ack_data = {
            "status": "connected",
            "device_id": device_id,
            "sid": sid,
            "timestamp": datetime.utcnow().isoformat(),
        }
        return ack_data

    except Exception as e:
        print(f"[ERROR] Error en connect: {str(e)}")
        raise e


@sio.event
async def disconnect(sid):
    """Maneja la desconexión de un cliente."""
    print(f"\n=== DESCONEXIÓN DETECTADA === SID: {sid}")
    try:
        # Buscar el dispositivo al que pertenece este SID
        device_id = None
        for dev_id, sids_set in list(active_connections.items()):
            if sid in sids_set:
                device_id = dev_id
                break

        if device_id:
            # Eliminar el SID del dispositivo
            active_connections[device_id].discard(sid)
            print(f"[DESCONEXIÓN] SID {sid} eliminado del dispositivo {device_id}")

            # Si no quedan más conexiones para este dispositivo, eliminarlo
            if not active_connections[device_id]:
                del active_connections[device_id]
                print(
                    f"[DESCONEXIÓN] Dispositivo {device_id} eliminado (sin conexiones)"
                )

            print(f"[DESCONEXIÓN] Estado actual: {active_connections}")
            print_connections()
        else:
            print(f"[DESCONEXIÓN] SID {sid} no encontrado en ninguna conexión activa")

    except Exception as e:
        print(f"[ERROR] Error en disconnect: {str(e)}")


@sio.event
async def message(sid, data):
    """
    Maneja los mensajes entrantes de los clientes y la API.

    Args:
        sid: ID de sesión del remitente (None si es de la API)
        data: Datos del mensaje, que debe ser un diccionario con:
            - message: Contenido del mensaje
            - sender_id: ID del remitente
            - room_id: ID de la sala/dispositivo destino
            - target_device_id: (opcional) ID específico del dispositivo
            - is_broadcast: (opcional) Si es True, se envía a todos los dispositivos
    """
    try:
        print(f"\n=== MENSAJE RECIBIDO === SID: {sid}")
        print(f"[MENSAJE] Data: {data}")
        print(f"[MENSAJE] Tipo de data: {type(data)}")

        # Verificar si el mensaje es un diccionario
        if not isinstance(data, dict):
            error_msg = f"El mensaje debe ser un diccionario, se recibió: {type(data)}"
            print(f"[ERROR] {error_msg}")
            return {"status": "error", "message": error_msg}

        # Obtener datos del mensaje
        message_text = data.get("message")
        room_id = data.get("room_id")
        target_device_id = data.get("target_device_id")
        is_broadcast = data.get("is_broadcast", False)
        sender_id = data.get("sender_id", "server")

        # Validar datos requeridos
        if not message_text:
            error_msg = "El campo 'message' es requerido"
            print(f"[ERROR] {error_msg}")
            return {"status": "error", "message": error_msg}

        if not room_id and not target_device_id and not is_broadcast:
            error_msg = "Se requiere al menos uno de: room_id, target_device_id o is_broadcast=True"
            print(f"[ERROR] {error_msg}")
            return {"status": "error", "message": error_msg}

        # Preparar el payload del mensaje
        payload = {
            "message": message_text,
            "timestamp": datetime.utcnow().isoformat(),
            "sender_id": sender_id,
            "room_id": room_id,
            "is_broadcast": is_broadcast,
        }

        # Determinar a quién enviar el mensaje
        recipients = set()

        if is_broadcast:
            # Enviar a todos los dispositivos conectados
            for device_id in active_connections.keys():
                recipients.update(active_connections[device_id])
            print(
                f"[BROADCAST] Enviando a todos los dispositivos: {len(recipients)} destinatarios"
            )
        elif target_device_id:
            # Enviar a un dispositivo específico
            if target_device_id in active_connections:
                recipients.update(active_connections[target_device_id])
                print(f"[TARGET] Enviando al dispositivo {target_device_id}")
            else:
                print(
                    f"[WARNING] Dispositivo destino no encontrado: {target_device_id}"
                )
        elif room_id:
            # Enviar a una sala específica (que en nuestro caso es lo mismo que el device_id)
            if room_id in active_connections:
                recipients.update(active_connections[room_id])
                print(f"[ROOM] Enviando a la sala {room_id}")
            else:
                print(f"[WARNING] Sala no encontrada: {room_id}")

        # Enviar el mensaje a los destinatarios
        if recipients:
            await sio.emit("message", payload, room=list(recipients))
            print(
                f"[ENVÍO] Mensaje enviado a {len(recipients)} destinatarios: {recipients}"
            )
        else:
            print("[ADVERTENCIA] No hay destinatarios para el mensaje")

        # Preparar respuesta
        response = {
            "status": "success",
            "message": "Mensaje procesado correctamente",
            "recipient_count": len(recipients),
            "timestamp": datetime.utcnow().isoformat(),
            "sent_to": target_device_id or room_id or "broadcast",
        }

        # Si es una solicitud de la API (sid=None), devolver la respuesta
        if sid is None:
            return response

        # Si es un mensaje de un cliente, enviar confirmación
        await sio.emit("message_response", response, room=sid)
        return response

    except Exception as e:
        error_msg = f"Error al procesar el mensaje: {str(e)}"
        print(f"[ERROR] {error_msg}")
        import traceback

        print(f"[ERROR] Traceback: {traceback.format_exc()}")

        # Enviar error al remitente si es un cliente
        if sid is not None:
            error_response = {
                "status": "error",
                "message": error_msg,
                "timestamp": datetime.utcnow().isoformat(),
            }
            await sio.emit("error", error_response, room=sid)

        return {"status": "error", "message": error_msg}


def get_active_connections() -> Dict[str, Set[str]]:
    """Devuelve el diccionario de conexiones activas."""
    return active_connections


def get_sio_instance():
    """Devuelve la instancia de Socket.IO."""
    return sio


def get_command_manager() -> "SocketCommandManager":
    """Devuelve la instancia del gestor de comandos."""
    return command_manager


class SocketCommandManager:
    """Clase para gestionar el envío de comandos a través de WebSockets."""

    def __init__(self, sio):
        """Inicializa el gestor de comandos con la instancia de Socket.IO."""
        self.sio = sio

    async def send_command(
        self,
        device_id: str,
        command: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Envía un comando a un dispositivo específico.

        Args:
            device_id: ID del dispositivo (room) destino
            command: Tipo de comando (BLOCK, LOCATE, etc.)
            data: Datos adicionales del comando
            **kwargs: Argumentos adicionales para el comando

        Returns:
            Dict con el resultado de la operación
        """
        if data is None:
            data = {}

        # Combinar datos adicionales
        command_data = {**data, **kwargs}

        # Crear el payload del comando
        payload = {
            "command": command,
            "timestamp": datetime.utcnow().isoformat(),
            "data": command_data,
        }

        try:
            # Verificar si el dispositivo está conectado
            active_connections = get_active_connections()
            if device_id not in active_connections or not active_connections[device_id]:
                return {
                    "status": "error",
                    "message": f"Dispositivo {device_id} no está conectado",
                    "command": command,
                    "device_id": device_id,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            # Enviar el comando al dispositivo
            await self.sio.emit("command", payload, room=device_id)
            print(
                f"[COMANDO] {command} enviado a {device_id}: {json.dumps(payload, indent=2)}"
            )

            return {
                "status": "success",
                "message": f"Comando {command} enviado exitosamente",
                "command": command,
                "device_id": device_id,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            error_msg = f"Error al enviar comando {command}: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "command": command,
                "device_id": device_id,
                "timestamp": datetime.utcnow().isoformat(),
            }

    # Comandos específicos

    async def block_device(self, device_id: str) -> Dict[str, Any]:
        """Envía un comando para bloquear un dispositivo."""
        return await self.send_command(device_id=device_id, command="BLOCK")

    async def unblock_device(
        self, device_id: str, reason: str = "", duration: int = 3600
    ) -> Dict[str, Any]:
        """Envía un comando para desbloquear un dispositivo."""
        return await self.send_command(
            device_id=device_id, command="UNBLOCK", reason=reason, duration=duration
        )

    async def locate_device(self, device_id: str, timeout: int = 30) -> Dict[str, Any]:
        """Solicita la ubicación actual de un dispositivo."""
        return await self.send_command(
            device_id=device_id, command="LOCATE", timeout=timeout
        )

    async def refresh_device(
        self, device_id: str, force: bool = False
    ) -> Dict[str, Any]:
        """Solicita una actualización de estado del dispositivo."""
        return await self.send_command(
            device_id=device_id, command="REFRESH", force=force
        )

    async def send_notification(
        self, device_id: str, title: str, message: str, priority: str = "normal"
    ) -> Dict[str, Any]:
        """Envía una notificación al dispositivo."""
        return await self.send_command(
            device_id=device_id,
            command="NOTIFY",
            title=title,
            message=message,
            priority=priority,
        )

    async def unenroll_device(self, device_id: str, reason: str = "") -> Dict[str, Any]:
        """Da de baja un dispositivo del sistema."""
        return await self.send_command(
            device_id=device_id, command="UN_ENROLL", reason=reason
        )

    async def report_exception(
        self,
        device_id: str,
        error_code: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Reporta una excepción desde el servidor al dispositivo."""
        if details is None:
            details = {}

        return await self.send_command(
            device_id=device_id,
            command="EXCEPTION",
            error_code=error_code,
            error_message=error_message,
            details=details,
        )


# Crear una instancia global del gestor de comandos
command_manager = SocketCommandManager(sio)


# Funciones de conveniencia para compatibilidad con código existente
async def send_command(device_id: str, command: str, **kwargs) -> Dict[str, Any]:
    """Función de conveniencia para enviar comandos (compatibilidad hacia atrás)."""
    return await command_manager.send_command(device_id, command, **kwargs)


async def block_device(device_id: str) -> Dict[str, Any]:
    """Envía un comando para bloquear un dispositivo."""
    return await command_manager.block_device(device_id)


async def unblock_device(device_id: str) -> Dict[str, Any]:
    """Envía un comando para desbloquear un dispositivo."""
    return await command_manager.unblock_device(device_id)


async def locate_device(device_id: str, timeout: int = 30) -> Dict[str, Any]:
    """Solicita la ubicación actual de un dispositivo."""
    return await command_manager.locate_device(device_id, timeout)


async def refresh_device(device_id: str, force: bool = False) -> Dict[str, Any]:
    """Solicita una actualización de estado del dispositivo."""
    return await command_manager.refresh_device(device_id, force)


async def send_notification(
    device_id: str, title: str, message: str, priority: str = "normal"
) -> Dict[str, Any]:
    """Envía una notificación al dispositivo."""
    return await command_manager.send_notification(device_id, title, message, priority)


async def unenroll_device(device_id: str, reason: str = "") -> Dict[str, Any]:
    """Da de baja un dispositivo del sistema."""
    return await command_manager.unenroll_device(device_id, reason)


async def report_exception(
    device_id: str,
    error_code: str,
    error_message: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Reporta una excepción desde el servidor al dispositivo."""
    return await command_manager.report_exception(
        device_id, error_code, error_message, details
    )


def get_connections_info() -> dict:
    """
    Devuelve información detallada sobre las conexiones activas.

    Returns:
        dict: Un diccionario con información detallada de las conexiones
    """
    connections_info = {}

    for device_id, sids in active_connections.items():
        connections_info[device_id] = {
            "connection_count": len(sids),
            "sids": list(sids),
            "last_updated": datetime.utcnow().isoformat(),
        }

    return connections_info
