from fastapi import APIRouter

from app.api.endpoints import auth, city, device, enrolment, plan, role, user
from app.routes import action, payment

api_router = APIRouter()

api_router.include_router(user.router, prefix="/users", tags=["Users"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(device.router, prefix="/devices", tags=["Devices"])
api_router.include_router(plan.router, prefix="/plans", tags=["Plans"])
api_router.include_router(enrolment.router, prefix="/enrolments", tags=["enrolments"])
api_router.include_router(city.router, prefix="/cities", tags=["cities"])
api_router.include_router(role.router, prefix="/roles", tags=["roles"])
api_router.include_router(payment.router, prefix="/payments", tags=["Payments"])
api_router.include_router(action.router, prefix="/actions", tags=["Actions"])
