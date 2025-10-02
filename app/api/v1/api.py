from fastapi import APIRouter

from app.api.endpoints import (
    account_type,
    analytics,
    auth,
    city,
    country,
    device,
    device_action,
    enrolment,
    plan,
    qr_enrollment,
    region,
    role,
    store,
    store_contact,
    user,
)
from app.routers import socket_router
from app.routes import (
    action,
    configuration,
    factory_reset_protection,
    google,
    payment,
    sim,
)

api_router = APIRouter()

api_router.include_router(action.router, prefix="/actions", tags=["actions"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(city.router, prefix="/cities", tags=["cities"])
api_router.include_router(
    configuration.router, prefix="/configurations", tags=["configurations"]
)
api_router.include_router(country.router, prefix="/countries", tags=["countries"])
api_router.include_router(device.router, prefix="/devices", tags=["devices"])
api_router.include_router(
    device_action.router, prefix="/device-actions", tags=["device-actions"]
)
api_router.include_router(socket_router.router)
api_router.include_router(enrolment.router, prefix="/enrolments", tags=["enrolments"])
api_router.include_router(
    factory_reset_protection.router,
    prefix="/factoryResetProtection",
    tags=["factoryResetProtection"],
)
api_router.include_router(google.router, prefix="/google", tags=["google"])
api_router.include_router(payment.router, prefix="/payments", tags=["payments"])
api_router.include_router(plan.router, prefix="/plans", tags=["plans"])
api_router.include_router(
    qr_enrollment.router, prefix="/qrEnrollment", tags=["qrEnrollment"]
)
api_router.include_router(region.router, prefix="/regions", tags=["regions"])
api_router.include_router(role.router, prefix="/roles", tags=["roles"])
api_router.include_router(sim.router, prefix="/sims", tags=["sims"])
api_router.include_router(store.router, prefix="/stores", tags=["stores"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(
    account_type.router, prefix="/account-types", tags=["account-types"]
)
api_router.include_router(store_contact.router, prefix="/store-contacts", tags=["store-contacts"])
