import traceback
from datetime import datetime

from fastapi import APIRouter

from app.servicios.socket import get_active_connections, get_connections_info

router = APIRouter()


@router.get("/connections")
async def get_connections():
    """
    Obtiene información detallada sobre las conexiones actuales.

    Incluye información sobre dispositivos conectados, sus sesiones y estadísticas.
    """
    try:
        print("\n=== SOLICITUD DE CONEXIONES ===")
        active_connections = get_active_connections()
        connections_info = get_connections_info()

        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "connected_devices": len(active_connections),
            "total_connections": sum(len(sids) for sids in active_connections.values()),
            "connections": connections_info,
            "debug": {"active_connections_keys": list(active_connections.keys())},
        }

    except Exception as e:
        error_msg = f"Error al obtener conexiones: {str(e)}"
        print(f"[ERROR] {error_msg}")
        traceback.print_exc()

        # Devolver el estado actual de las conexiones incluso en caso de error
        return {
            "status": "error",
            "message": error_msg,
            "server_time": datetime.utcnow().isoformat(),
            "connected_devices": len(active_connections),
            "total_connections": sum(len(s) for s in active_connections.values()),
            "active_connections_keys": list(active_connections.keys()),
        }
