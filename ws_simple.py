#!/usr/bin/env python3
"""
Cliente WebSocket simple usando solo bibliotecas estándar
Uso: python3 ws_simple.py [device_id]
"""

import base64
import json
import socket
import sys
import threading
import time
from urllib.parse import urlparse


class SimpleWebSocketClient:
    def __init__(self, url):
        self.url = url
        parsed = urlparse(url)
        self.host = parsed.hostname or "localhost"
        self.port = parsed.port or 8004
        self.path = parsed.path or "/"
        self.socket = None
        self.running = True

    def create_handshake(self):
        """Crear handshake WebSocket"""
        key = base64.b64encode(b"simple-client-key").decode()

        handshake = f"""GET {self.path} HTTP/1.1\r
Host: {self.host}:{self.port}\r
Upgrade: websocket\r
Connection: Upgrade\r
Sec-WebSocket-Key: {key}\r
Sec-WebSocket-Version: 13\r
\r
"""
        return handshake.encode()

    def connect(self):
        """Conectar al WebSocket"""
        try:
            print(f"🔌 Conectando a {self.url}")

            # Crear socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))

            # Enviar handshake
            handshake = self.create_handshake()
            self.socket.send(handshake)

            # Recibir respuesta
            response = self.socket.recv(1024).decode()

            if "101 Switching Protocols" in response:
                print("✅ ¡Conectado al WebSocket!")
                return True
            else:
                print("❌ Error en handshake WebSocket")
                print(response)
                return False

        except Exception as e:
            print(f"❌ Error conectando: {e}")
            return False

    def send_frame(self, message):
        """Enviar frame WebSocket"""
        try:
            if isinstance(message, str):
                message = message.encode("utf-8")

            # Frame simple (sin mask para simplicidad)
            length = len(message)
            if length < 126:
                frame = bytes([0x81, length]) + message
            else:
                frame = bytes([0x81, 126]) + length.to_bytes(2, "big") + message

            self.socket.send(frame)
            return True
        except Exception as e:
            print(f"❌ Error enviando: {e}")
            return False

    def receive_frame(self):
        """Recibir frame WebSocket"""
        try:
            # Leer header
            header = self.socket.recv(2)
            if len(header) < 2:
                return None

            opcode = header[0] & 0x0F
            length = header[1] & 0x7F

            # Leer longitud extendida si es necesario
            if length == 126:
                length_bytes = self.socket.recv(2)
                length = int.from_bytes(length_bytes, "big")

            # Leer payload
            payload = b""
            while len(payload) < length:
                chunk = self.socket.recv(length - len(payload))
                if not chunk:
                    break
                payload += chunk

            if opcode == 0x8:  # Close frame
                return None
            elif opcode == 0x1:  # Text frame
                return payload.decode("utf-8")

        except Exception as e:
            print(f"❌ Error recibiendo: {e}")
            return None

    def listen_messages(self):
        """Escuchar mensajes del servidor"""
        while self.running:
            try:
                message = self.receive_frame()
                if message is None:
                    break

                # Parsear JSON
                try:
                    data = json.loads(message)
                    msg_type = data.get("type", "MSG")
                    content = data.get("message", str(data))
                    timestamp = time.strftime("%H:%M:%S")

                    print(f"\n[{timestamp}] 📩 {msg_type.upper()}: {content}")
                    if "from_device" in data:
                        print(f"   👤 De: {data['from_device']}")
                    print("💬 > ", end="", flush=True)

                except json.JSONDecodeError:
                    print(f"\n📩 {message}")
                    print("💬 > ", end="", flush=True)

            except Exception as e:
                if self.running:
                    print(f"❌ Error: {e}")
                break

    def run(self, device_id):
        """Ejecutar cliente"""
        print("=" * 50)
        print("🚀 CLIENTE WEBSOCKET SIMPLE")
        print("=" * 50)
        print(f"🏷️  Device ID: {device_id}")
        print(f"🔌 URL: {self.url}")
        print("=" * 50)

        if not self.connect():
            return

        # Iniciar hilo para escuchar mensajes
        listener = threading.Thread(target=self.listen_messages)
        listener.daemon = True
        listener.start()

        print("\n💡 Escribe mensajes (quit para salir)")
        print("💬 > ", end="", flush=True)

        try:
            while self.running:
                message = input()

                if message.lower() in ["quit", "exit", "q"]:
                    print("👋 Desconectando...")
                    break

                if message.strip():
                    if self.send_frame(message):
                        print(f"📤 Enviado: {message}")
                    print("💬 > ", end="", flush=True)

        except KeyboardInterrupt:
            print("\n👋 Desconectando...")
        except EOFError:
            print("👋 Desconectando...")
        finally:
            self.running = False
            if self.socket:
                self.socket.close()


if __name__ == "__main__":
    device_id = sys.argv[1] if len(sys.argv) > 1 else "simple-client"
    url = f"ws://localhost:8004/ws/{device_id}"

    client = SimpleWebSocketClient(url)
    client.run(device_id)
