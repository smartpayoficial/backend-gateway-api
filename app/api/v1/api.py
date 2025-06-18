from fastapi import APIRouter

from app.api.endpoints import auth, city, device, enrolment, user

api_router = APIRouter()

api_router.include_router(user.router, tags=["users"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(device.router, prefix="/devices", tags=["devices"])
api_router.include_router(enrolment.router, prefix="/enrolments", tags=["enrolments"])
api_router.include_router(city.router, prefix="/cities", tags=["cities"])
