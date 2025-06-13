from fastapi import APIRouter

from app.api.endpoints import auth, broadcast, connections, device_commands, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(connections.router, tags=["connections"])
api_router.include_router(broadcast.router, tags=["broadcast"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(
    device_commands.router, prefix="/devices", tags=["device-commands"]
)
