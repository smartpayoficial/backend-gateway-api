import asyncio
import json
import sys

import websockets


async def test_websocket():
    uri = "ws://localhost:8000/ws/test_device"

    try:
        async with websockets.connect(uri) as websocket:
            print("Conectado al WebSocket")

            # Recibir mensaje de bienvenida
            response = await websocket.recv()
            print(f"Respuesta del servidor: {response}")

            # Enviar un mensaje de prueba
            test_message = {
                "action": "echo",
                "data": "¡Hola desde el cliente de prueba!",
            }
            await websocket.send(json.dumps(test_message))

            # Recibir eco
            response = await websocket.recv()
            print(f"Eco recibido: {response}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test_websocket())
