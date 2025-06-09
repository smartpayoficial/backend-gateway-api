import os
import sys
from datetime import datetime
from typing import Dict, Optional, Set

import socketio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configuración de la aplicación FastAPI
app = FastAPI(title="SmartPay Gateway API")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Inicializando Socket.IO...")

# Mapa para mantener el seguimiento de las conexiones
active_connections: Dict[str, Set[str]] = {}


class MessageRequest(BaseModel):
    """Modelo de entrada para envío de mensajes."""

    message: str
    sender_id: Optional[str] = None
    room_id: str
    device_id: Optional[str] = None


# Función para imprimir el estado de las conexiones
def print_connections():
    print("\n=== ESTADO DE CONEXIONES ===")
    for device_id, sids in active_connections.items():
        print(f"Device {device_id} tiene {len(sids)} conexiones")
    print("===========================\n")


# Configuración de Socket.IO
print("Inicializando Socket.IO...")
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True,
    ping_timeout=60,  # Tiempo de espera para respuesta PONG (ms)
    ping_interval=25,  # Intervalo entre PINGs (segundos)
    max_http_buffer_size=1e6,
    async_handlers=True,
    # Configuraciones adicionales para mejorar compatibilidad
    allow_upgrades=True,
    http_compression=False,  # Desactivar compresión para simplificar
    compression_threshold=0,  # Desactivar umbral de compresión
    cookie=None,
    cors_credentials=True,
    namespaces=["/"],
    always_connect=False,
    reconnection=True,
    reconnection_attempts=3,
    reconnection_delay=1,
    reconnection_delay_max=5,
    randomization_factor=0.5,
    # Configuración específica para WebSocket
    websocket_extra_headers={"Access-Control-Allow-Origin": "*"},
    # Deshabilitar la verificación de orígenes para pruebas
    cors_allowed_headers=["*"],
    # Asegurar que los mensajes se envíen en modo binario
    binary=False,  # Usar mensajes de texto en lugar de binarios
    # Configuración de timeouts
    request_timeout=60,  # Tiempo de espera para solicitudes HTTP
    # Configuración de sesiones
    manage_http_sessions=False,  # No gestionar sesiones HTTP
)

# Registrar manejadores de eventos manualmente
print("\n=== REGISTRANDO MANEJADORES MANUALMENTE ===")

# Crear aplicación ASGI para Socket.IO
socket_app = socketio.ASGIApp(sio, socketio_path="/socket.io")


# Registrar eventos manualmente
@sio.on("connect")
async def on_connect(sid, environ, auth):
    print(
        f"\n=== MANUAL CONNECT HANDLER TRIGGERED === SID: {sid} Environ: {environ} Auth: {auth}"
    )
    return await connect(sid, environ, auth)


@sio.on("disconnect")
async def on_disconnect(sid):
    print(f"\n=== MANUAL DISCONNECT HANDLER TRIGGERED === SID: {sid}")
    return await handle_disconnect(sid)


@sio.on("message")
async def on_message(sid, data):
    print(f"\n=== MANUAL MESSAGE HANDLER TRIGGERED === SID: {sid} Data: {data}")
    return await handle_message(sid, data)


# Montar la aplicación de Socket.IO en FastAPI
app.mount("/socket.io", socket_app)

print("Aplicación Socket.IO configurada correctamente")

# Registrar manejadores de eventos
print("\n=== REGISTRANDO MANEJADORES DE EVENTOS ===")
print(f"[SOCKET.IO] Manejadores antes de registrar: {sio.handlers}")

# Eventos de Socket.IO
print("\n=== DEFINICIÓN DE MANEJADORES DE EVENTOS ===")


@sio.event
async def connect(sid, environ, auth):
    try:
        print("\n" + "=" * 50)
        print("=== NUEVA CONEXIÓN DETECTADA ===")
        print(f"[CONEXIÓN] SID: {sid}")
        print(f"[CONEXIÓN] Time: {datetime.utcnow().isoformat()}")
        print(f"[CONEXIÓN] Remote IP: {environ.get('REMOTE_ADDR', 'unknown')}")
        print(f"[CONEXIÓN] Environ keys: {list(environ.keys())}")
        print(f"[CONEXIÓN] Auth: {auth}")
        print(
            f"[CONEXIÓN] Headers: { {k: v for k, v in environ.items() if k.startswith('HTTP_')} }"
        )

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

        # Registrar la conexión
        print(f"[CONEXIÓN] Estado ANTES de registrar conexión: {active_connections}")

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
            "sid": sid,
            "device_id": device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Conexión establecida correctamente",
            "server_time": datetime.utcnow().isoformat(),
            "active_connections": {k: len(v) for k, v in active_connections.items()},
        }

        # Enviar confirmación de conexión
        try:
            print(f"[CONEXIÓN] Enviando ACK a SID: {sid}")
            await sio.emit("connection_ack", ack_data, room=sid)
            print(f"[CONEXIÓN] Confirmación enviada a {sid}")

            # Enviar un ping de prueba
            print(f"[CONEXIÓN] Enviando PING a SID: {sid}")
            await sio.emit(
                "ping", {"server_time": datetime.utcnow().isoformat()}, room=sid
            )
            print(f"[CONEXIÓN] Ping enviado a {sid}")

            # Forzar actualización de la lista de conexiones
            print(
                "[CONEXIÓN] Enviando actualización de conexiones a todos los clientes"
            )
            await sio.emit(
                "connections_updated",
                {
                    "connected_devices": len(active_connections),
                    "total_connections": sum(
                        len(sids) for sids in active_connections.values()
                    ),
                    "timestamp": datetime.utcnow().isoformat(),
                    "active_connections": {
                        k: len(v) for k, v in active_connections.items()
                    },
                },
            )

            print("[CONEXIÓN] Conexión completada exitosamente")
            return True

        except Exception as e:
            error_msg = f"[ERROR] Error al enviar confirmación a {sid}: {str(e)}"
            print(error_msg)
            import traceback

            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return False

    except Exception as e:
        error_msg = f"[ERROR] Error en connect: {str(e)}"
        print(error_msg)
        import traceback

        print(f"[ERROR] Traceback: {traceback.format_exc()}")

        if "sid" in locals():
            try:
                await sio.emit("error", {"message": error_msg}, room=sid)
            except Exception as emit_error:
                print(f"[ERROR] No se pudo enviar mensaje de error: {str(emit_error)}")
        return False


@sio.on("disconnect")
async def handle_disconnect(sid):
    """Maneja la desconexión de un cliente."""
    try:
        print("\n=== DESCONEXIÓN DETECTADA ===")
        print(f"[DESCONEXIÓN] SID: {sid}")
        print(f"[DESCONEXIÓN] Time: {datetime.utcnow().isoformat()}")

        # Buscar y eliminar el SID de todas las entradas
        disconnected_device = None
        for device_id, sids in list(active_connections.items()):
            if sid in sids:
                sids.remove(sid)
                disconnected_device = device_id
                print(f"[DESCONEXIÓN] Desconectado de dispositivo: {device_id}")

                # Si no quedan más conexiones para este dispositivo, eliminar la entrada
                if not sids:
                    del active_connections[device_id]
                    print(
                        f"[DESCONEXIÓN] No hay más conexiones para el dispositivo {device_id}, eliminando..."
                    )

                break

        # Notificar a otros clientes sobre la desconexión
        if disconnected_device:
            try:
                # Notificar solo a los dispositivos afectados
                if disconnected_device in active_connections:
                    await sio.emit(
                        "peer_disconnected",
                        {
                            "device_id": disconnected_device,
                            "sid": sid,
                            "timestamp": datetime.utcnow().isoformat(),
                            "message": f"Dispositivo {disconnected_device} desconectado",
                            "remaining_connections": len(
                                active_connections.get(disconnected_device, [])
                            ),
                        },
                        room=disconnected_device,
                        skip_sid=sid,
                    )

                # Notificar a todos los clientes sobre la actualización de conexiones
                await sio.emit(
                    "connections_updated",
                    {
                        "connected_devices": len(active_connections),
                        "total_connections": sum(
                            len(sids) for sids in active_connections.values()
                        ),
                        "timestamp": datetime.utcnow().isoformat(),
                        "active_connections": {
                            k: len(v) for k, v in active_connections.items()
                        },
                    },
                )

                print(
                    f"[DESCONEXIÓN] Notificaciones de desconexión enviadas para SID: {sid}"
                )

            except Exception as e:
                print(f"[ERROR] Error al notificar desconexión: {str(e)}")

        print_connections()
        return True

    except Exception as e:
        error_msg = f"Error en handle_disconnect: {str(e)}"
        print(f"[ERROR] {error_msg}")
        try:
            if "sid" in locals():
                await sio.emit("error", {"message": error_msg}, room=sid)
        except Exception as emit_error:
            print(f"[ERROR] No se pudo enviar mensaje de error: {str(emit_error)}")
        return False


@sio.on("message")
async def handle_message(sid, data):
    """Maneja los mensajes entrantes de los clientes."""
    try:
        print("\n=== MENSAJE RECIBIDO ===")
        print(f"[MENSAJE] De: {sid}")
        print(f"[MENSAJE] Contenido: {data}")

        # Manejar mensajes especiales
        if isinstance(data, dict):
            if data.get("type") == "pong":
                print(f"[PONG] Recibido de {sid}")
                return
            elif data.get("type") == "ping":
                await sio.emit(
                    "pong", {"server_time": datetime.utcnow().isoformat()}, room=sid
                )
                return

        # Mensaje normal - hacer eco
        await sio.emit(
            "message",
            {
                "type": "echo",
                "message": data,
                "timestamp": datetime.utcnow().isoformat(),
                "sid": sid,
                "server_time": datetime.utcnow().isoformat(),
            },
            room=sid,
        )

    except Exception as e:
        error_msg = f"[ERROR] Error en handle_message: {str(e)}"
        print(error_msg)
        try:
            await sio.emit("error", {"message": error_msg}, room=sid)
        except Exception:
            return False


# Verificar manejadores registrados después de la definición
print("\n=== VERIFICACIÓN DE MANEJADORES REGISTRADOS ===")
print(f"[SOCKET.IO] Manejadores después de registrar: {sio.handlers}")
print("=========================================\n")


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
    """
    Endpoint de verificación de salud.

    Retorna el estado actual del servidor y estadísticas de conexiones.
    """
    try:
        total_connections = sum(len(sids) for sids in active_connections.values())

        return {
            "status": "healthy",
            "server_time": datetime.utcnow().isoformat(),
            "server_utc_offset": datetime.now().astimezone().strftime("%z"),
            "connected_devices": len(active_connections),
            "total_connections": total_connections,
            "active_connections": [
                {
                    "device_id": device_id,
                    "connection_count": len(sids),
                    "last_active": max(
                        [
                            sio.manager.get_participants("/", sid)[0].last_ping_time
                            for sid in sids
                            if sid in sio.manager.get_participants("/", None)
                        ],
                        default=datetime.utcnow().isoformat(),
                    ),
                }
                for device_id, sids in active_connections.items()
            ],
            "server_info": {
                "python_version": ".".join(map(str, sys.version_info[:3])),
                "socketio_version": "5.11.2",
                "fastapi_version": "0.68.0",
                "environment": os.getenv("ENVIRONMENT", "development"),
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


@app.get("/connections")
async def get_connections():
    """
    Obtiene información detallada sobre las conexiones actuales.

    Incluye información sobre dispositivos conectados, sus sesiones y estadísticas.
    """
    try:
        print("\n=== SOLICITUD DE CONEXIONES ===")
        print(f"[CONEXIONES] Diccionario active_connections: {active_connections}")

        # Obtener información detallada de las conexiones
        connections_info = []
        total_connections = 0

        # Crear una copia del diccionario para evitar problemas de concurrencia
        current_connections = dict(active_connections)

        for device_id, sids in current_connections.items():
            device_connections = []

            # Crear una copia del conjunto de SIDs para evitar problemas de concurrencia
            sids_copy = set(sids)

            for sid in sids_copy:
                # Obtener información de la sesión
                session_info = {
                    "sid": sid,
                    "connected_since": None,
                    "last_ping": None,
                    "transport": None,
                    "status": "active",
                }

                # Verificar si el SID sigue activo en el gestor de Socket.IO
                try:
                    # Obtener información del socket desde el gestor de Socket.IO
                    sockets = sio.manager.get_participants("/", sid)
                    if sockets:
                        socket = sockets[0]
                        session_info.update(
                            {
                                "connected_since": getattr(
                                    socket, "connected_at", None
                                ),
                                "last_ping": getattr(socket, "last_ping_time", None),
                                "transport": getattr(socket, "transport", "websocket"),
                                "last_packet": getattr(
                                    socket, "last_packet_received", None
                                ),
                            }
                        )

                        # Verificar si la conexión sigue activa
                        if hasattr(socket, "closed") and socket.closed:
                            session_info["status"] = "closed"
                            # Eliminar SID inactivo
                            if sid in active_connections.get(device_id, set()):
                                active_connections[device_id].remove(sid)
                                if not active_connections[device_id]:
                                    del active_connections[device_id]
                            continue
                    else:
                        # Si no se encuentra en el gestor, marcar como inactivo
                        session_info["status"] = "not_found"
                        # Eliminar SID no encontrado
                        if sid in active_connections.get(device_id, set()):
                            active_connections[device_id].remove(sid)
                            if not active_connections[device_id]:
                                del active_connections[device_id]
                        continue

                except Exception as e:
                    print(f"[WARN] Error al obtener información para SID {sid}: {e}")
                    session_info["status"] = f"error: {str(e)}"

                device_connections.append(session_info)

            # Solo incluir dispositivos con conexiones activas
            if device_id in active_connections and active_connections[device_id]:
                connections_info.append(
                    {
                        "device_id": device_id,
                        "connection_count": len(active_connections[device_id]),
                        "sessions": device_connections,
                    }
                )
                total_connections += len(active_connections[device_id])

        # Crear respuesta con información detallada
        response = {
            "status": "success",
            "server_time": datetime.utcnow().isoformat(),
            "connected_devices": len(active_connections),
            "total_connections": total_connections,
            "devices": connections_info,
            "server_info": {
                "socketio_path": "/socket.io",
                "ping_interval": 25,
                "ping_timeout": 60,
                "max_http_buffer_size": 1e8,
            },
            "debug": {
                "active_connections_keys": list(active_connections.keys()),
                "connection_counts": {k: len(v) for k, v in active_connections.items()},
            },
        }

        print(
            f"[INFO] Estado de conexiones: {len(active_connections)} dispositivos, {total_connections} conexiones totales"
        )
        print(f"[DEBUG] Respuesta completa: {response}")

        return response

    except Exception as e:
        error_msg = f"Error al obtener conexiones: {str(e)}"
        import traceback

        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")

        # Devolver el estado actual de las conexiones incluso en caso de error
        return {
            "status": "error",
            "message": error_msg,
            "server_time": datetime.utcnow().isoformat(),
            "connected_devices": len(active_connections),
            "total_connections": sum(len(s) for s in active_connections.values()),
            "active_connections_keys": list(active_connections.keys()),
            "error_details": str(e),
            "traceback": traceback.format_exc(),
        }


@app.post("/broadcast")
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
        # Validar que hay conexiones activas si no es un mensaje de broadcast
        if message_request.room_id != "broadcast" and not active_connections:
            raise HTTPException(
                status_code=404, detail="No hay dispositivos conectados"
            )

        # Construir el mensaje
        message = {
            "type": "broadcast",
            "message": message_request.message,
            "sender_id": message_request.sender_id or "server",
            "room_id": message_request.room_id,
            "device_id": message_request.device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "server_time": datetime.utcnow().isoformat(),
        }

        # Determinar los destinatarios
        recipients = 0

        if message_request.room_id == "broadcast":
            # Enviar a todos los clientes conectados
            for device_id, sids in active_connections.items():
                await sio.emit("message", message, room=list(sids))
                recipients += len(sids)
                print(
                    f"[BROADCAST] Enviado a dispositivo {device_id} ({len(sids)} conexiones)"
                )

        elif message_request.device_id:
            # Enviar a un dispositivo específico
            if message_request.device_id in active_connections:
                sids = active_connections[message_request.device_id]
                await sio.emit("message", message, room=list(sids))
                recipients = len(sids)
                print(
                    f"[MESSAGE] Enviado a dispositivo {message_request.device_id} ({recipients} conexiones)"
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Dispositivo {message_request.device_id} no encontrado o desconectado",
                )
        else:
            # Enviar a una sala específica
            room = message_request.room_id
            await sio.emit("message", message, room=room)
            # Contar conexiones en la sala
            recipients = sum(
                len(sids)
                for device_id, sids in active_connections.items()
                if any(sid in sio.manager.rooms.get(f"/{sid}", {}) for sid in sids)
            )
            print(f"[ROOM_MESSAGE] Enviado a sala {room} ({recipients} conexiones)")

        # Registrar el envío
        print(f"[BROADCAST] Mensaje enviado a {recipients} destinatarios: {message}")

        return {
            "status": "message_sent",
            "message": "Mensaje enviado exitosamente",
            "recipients": recipients,
            "room_id": message_request.room_id,
            "device_id": message_request.device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "server_time": datetime.utcnow().isoformat(),
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = f"Error al enviar mensaje: {str(e)}"
        print(f"[ERROR] {error_msg}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": error_msg,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
