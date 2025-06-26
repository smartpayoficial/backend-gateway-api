from typing import List

from fastapi import WebSocket


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
