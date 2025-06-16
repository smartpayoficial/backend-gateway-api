from fastapi import APIRouter

from app.api.endpoints import auth, device, user

api_router = APIRouter()

api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(device.router, prefix="/devices", tags=["devices"])
