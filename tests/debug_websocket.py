"""
Script de depuración para probar la conexión WebSocket con el servidor.

Este script utiliza el cliente de Socket.IO para conectarse al servidor y verificar
que los eventos se estén manejando correctamente.
"""

import asyncio
import logging

import socketio

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL del servidor WebSocket
SERVER_URL = "http://localhost:8000"
DEVICE_ID = "test-device-123"

# Crear cliente Socket.IO
sio = socketio.AsyncClient()


@sio.event
async def connect():
    """Manejador de evento de conexión exitosa."""
    logger.info("Conectado al servidor con SID: %s", sio.sid)

    # Unirse a una sala específica para este dispositivo
    await sio.emit("join", {"device_id": DEVICE_ID})
    logger.info("Dispositivo %s unido a la sala", DEVICE_ID)


@sio.event
async def connect_error(data):
    """Manejador de errores de conexión."""
    logger.error("Error de conexión: %s", data)


@sio.event
async def disconnect():
    """Manejador de desconexión."""
    logger.info("Desconectado del servidor")


@sio.event
async def message(data):
    """Manejador de mensajes recibidos."""
    logger.info("Mensaje recibido: %s", data)


@sio.event
async def connection_ack(data):
    """Manejador de confirmación de conexión."""
    logger.info("Confirmación de conexión recibida: %s", data)


async def main():
    """Función principal para probar la conexión WebSocket."""
    try:
        # Conectar al servidor con parámetros de consulta
        logger.info("\n=== INICIANDO CONEXIÓN WEBSOCKET ===")
        logger.info("Conectando a %s con device_id=%s", SERVER_URL, DEVICE_ID)

        # Construir la URL con los parámetros de consulta
        url = f"{SERVER_URL}/socket.io/?device_id={DEVICE_ID}"

        # Conectar usando la URL con parámetros
        await sio.connect(
            url,
            socketio_path="/socket.io",
            transports=["websocket"],
            namespaces=["/"],
            auth={"token": "debug-token"},
        )

        # Mantener la conexión abierta
        await sio.wait()

    except Exception as e:
        logger.error("Error: %s", str(e))
    finally:
        await sio.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
