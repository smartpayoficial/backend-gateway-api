import json
from uuid import UUID

from fastapi import APIRouter, Response, status

router = APIRouter() 

@router.get("/")
async def get_qr_enrollment(enrollment_id: UUID, store_id: UUID, re_enrollment: bool):
    return {
        "android.app.extra.PROVISIONING_DEVICE_ADMIN_COMPONENT_NAME": "com.olimpo.smartpay/com.olimpo.smartpay.receivers.SmartPayDeviceAdminReceiver",
        "android.app.extra.PROVISIONING_DEVICE_ADMIN_SIGNATURE_CHECKSUM": "j2ZASIJBbIEXGtqQvvgdECA0_Knw4QDjZIVwLWa9unw=",
        "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_DOWNLOAD_LOCATION": "https://appincdevs.com/enterprise/smartpay-google.apk",
        "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_CHECKSUM": "j2ZASIJBbIEXGtqQvvgdECA0_Knw4QDjZIVwLWa9unw=",
        "android.app.extra.PROVISIONING_LEAVE_ALL_SYSTEM_APPS_ENABLED": True,
        "android.app.extra.PROVISIONING_LOCALE": "es_ES",
        "android.app.extra.PROVISIONING_ADMIN_EXTRAS_BUNDLE": {
            "ENROLLMENT_ID": str(enrollment_id),
            "STORE_ID": str(store_id),
            "RE_ENROLLMENT": re_enrollment
        }
    }