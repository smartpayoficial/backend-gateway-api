import os
import sys
from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.servicios.socket import get_active_connections

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Endpoint de verificación de salud.

    Retorna el estado actual del servidor y estadísticas de conexiones.
    """
    try:
        active_connections = get_active_connections()
        return {
            "status": "healthy",
            "server_time": datetime.utcnow().isoformat(),
            "server_utc_offset": datetime.now().astimezone().strftime("%z"),
            "connected_devices": len(active_connections),
            "total_connections": sum(len(sids) for sids in active_connections.values()),
            "server_info": {
                "python_version": ".".join(map(str, sys.version_info[:3])),
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
