from fastapi import APIRouter

from app.api.endpoints import auth, city, device, enrolment, role, user

api_router = APIRouter()

api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(device.router, prefix="/devices", tags=["devices"])
api_router.include_router(enrolment.router, prefix="/enrolments", tags=["enrolments"])
api_router.include_router(city.router, prefix="/cities", tags=["cities"])
api_router.include_router(role.router, prefix="/roles", tags=["roles"])
