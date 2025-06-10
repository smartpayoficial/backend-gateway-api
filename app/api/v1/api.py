from fastapi import APIRouter

from app.api.endpoints import broadcast, connections, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(connections.router, tags=["connections"])
api_router.include_router(broadcast.router, tags=["broadcast"])
