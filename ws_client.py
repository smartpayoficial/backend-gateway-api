#!/usr/bin/env python3
"""
Cliente WebSocket para probar SimpleAPI
Uso: python3 ws_client.py [device_id]
"""

import asyncio
import json
import signal
import sys
from datetime import datetime

try:
    import websockets
except ImportError:
    print("📦 Instalando websockets...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets"])
    import websockets


class WebSocketClient:
    def __init__(self, device_id="terminal-client"):
        self.device_id = device_id
        self.uri = f"ws://localhost:8004/ws/{device_id}"
        self.websocket = None
        self.running = True

    def print_header(self):
        print("=" * 60)
        print("🚀 CLIENTE WEBSOCKET - SIMPLE API")
        print("=" * 60)
        print(f"🏷️  Device ID: {self.device_id}")
        print(f"🔌 URI: {self.uri}")
        print("=" * 60)

    def print_message(self, msg_type, content, extra_info=None):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] 📩 {msg_type.upper()}: {content}")

        if extra_info:
            for key, value in extra_info.items():
                print(f"   {key}: {value}")

    async def handle_messages(self):
        """Maneja los mensajes entrantes del WebSocket"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type", "MESSAGE")
                    content = data.get("message", str(data))

                    extra_info = {}
                    if "from_device" in data:
                        extra_info["👤 De"] = data["from_device"]
                    if "timestamp" in data:
                        extra_info["🕒 Timestamp"] = data["timestamp"]
                    if "connected_devices" in data:
                        extra_info["👥 Dispositivos conectados"] = data[
                            "connected_devices"
                        ]
                    if "recipients" in data:
                        extra_info["📡 Destinatarios"] = data["recipients"]

                    self.print_message(msg_type, content, extra_info)

                except json.JSONDecodeError:
                    self.print_message("RAW", message)

        except websockets.exceptions.ConnectionClosed:
            print("\n🔴 Conexión cerrada por el servidor")
        except Exception as e:
            print(f"\n❌ Error recibiendo mensajes: {e}")

    async def send_message_loop(self):
        """Loop para enviar mensajes desde la terminal"""
        print("\n💡 Comandos disponibles:")
        print("   - Escribe cualquier mensaje y presiona Enter")
        print("   - 'quit' o 'exit' para salir")
        print("   - 'ping' para enviar un ping")
        print("   - Ctrl+C para salir")
        print("\nEscribe tus mensajes:\n")

        try:
            while self.running:
                try:
                    message = await asyncio.get_event_loop().run_in_executor(
                        None, input, "💬 > "
                    )

                    if message.lower() in ["quit", "exit", "q"]:
                        print("👋 Desconectando...")
                        self.running = False
                        break

                    if message.strip():
                        await self.websocket.send(message)
                        print(f"📤 Enviado: {message}")

                except EOFError:
                    break

        except KeyboardInterrupt:
            print("\n\n👋 Desconectando por Ctrl+C...")
            self.running = False

    async def connect_and_run(self):
        """Conecta al WebSocket y ejecuta el cliente"""
        self.print_header()
        print("🔌 Conectando...")

        try:
            async with websockets.connect(self.uri) as websocket:
                self.websocket = websocket
                print("✅ ¡CONECTADO EXITOSAMENTE!")
                print("🎯 Esperando mensajes del servidor...")

                # Ejecutar ambas tareas en paralelo
                await asyncio.gather(
                    self.handle_messages(),
                    self.send_message_loop(),
                    return_exceptions=True,
                )

        except ConnectionRefusedError:
            print("❌ ERROR: No se pudo conectar al WebSocket")
            print("   Verifica que el servidor esté ejecutándose:")
            print("   http://localhost:8004")

        except Exception as e:
            print(f"❌ Error inesperado: {e}")

        finally:
            print("\n🔴 Desconectado del WebSocket")

    def run(self):
        """Punto de entrada principal"""

        # Configurar manejo de señales
        def signal_handler(signum, frame):
            print("\n\n👋 Señal de salida recibida...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            asyncio.run(self.connect_and_run())
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")


def show_help():
    """Muestra la ayuda del cliente"""
    print(
        """
🚀 CLIENTE WEBSOCKET - SIMPLE API

USO:
    python3 ws_client.py [device_id]

EJEMPLOS:
    python3 ws_client.py                    # device_id por defecto: 'terminal-client'
    python3 ws_client.py mi-dispositivo     # device_id personalizado
    python3 ws_client.py device1            # para pruebas múltiples

COMANDOS EN EL CLIENTE:
    - Cualquier texto: Se envía como mensaje
    - 'quit' o 'exit': Salir del cliente
    - 'ping': Enviar mensaje de ping
    - Ctrl+C: Salir del cliente

PRUEBA BROADCAST (desde otra terminal):
    curl -X POST http://localhost:8004/broadcast \\
      -H "Content-Type: application/json" \\
      -d '{"message": "¡Hola a todos!", "device_id": "servidor"}'

VER CONEXIONES ACTIVAS:
    curl http://localhost:8004/connections

HEALTH CHECK:
    curl http://localhost:8004
    """
    )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        show_help()
        sys.exit(0)

    device_id = sys.argv[1] if len(sys.argv) > 1 else "terminal-client"

    client = WebSocketClient(device_id)
    client.run()
