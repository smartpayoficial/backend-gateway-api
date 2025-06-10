"""
Módulo para manejar la lógica de WebSockets con Socket.IO.
"""

from datetime import datetime
from typing import Dict, Set

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
    """Maneja los mensajes entrantes de los clientes."""
    try:
        print(f"\n=== MENSAJE RECIBIDO === SID: {sid}")
        print(f"[MENSAJE] Data: {data}")
        print(f"[MENSAJE] Tipo de data: {type(data)}")

        # Verificar si el mensaje es un diccionario
        if not isinstance(data, dict):
            print(f"[MENSAJE] El mensaje no es un diccionario: {data}")
            return {"status": "error", "message": "El mensaje debe ser un diccionario"}

        # Enviar respuesta de confirmación
        response = {
            "status": "received",
            "message": "Mensaje recibido correctamente",
            "data_received": data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        return response

    except Exception as e:
        print(f"[ERROR] Error en message: {str(e)}")
        return {"status": "error", "message": f"Error al procesar el mensaje: {str(e)}"}


def get_active_connections() -> Dict[str, Set[str]]:
    """Devuelve el diccionario de conexiones activas."""
    return active_connections


def get_sio_instance():
    """Devuelve la instancia de Socket.IO."""
    return sio


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
