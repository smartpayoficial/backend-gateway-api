import logging

from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import RedirectResponse 
import requests, os, urllib.parse

from app.models.factory_reset_protection import FactoryResetProtectionCreate, FactoryResetProtectionState
from app.servicios import factory_reset_protection as factory_reset_protection_service

router = APIRouter(tags=["google"])

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

@router.get("/auth/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")

    logging.error(
                f"Google - {CLIENT_ID} - {CLIENT_SECRET} - {REDIRECT_URI}."
            )

    # 1. Obtener el token
    token_res = requests.post("https://oauth2.googleapis.com/token", data={
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    })

    access_token = token_res.json().get("access_token")

    # 2. Obtener datos del perfil con People API
    people_res = requests.get(
        "https://people.googleapis.com/v1/people/me?personFields=names,emailAddresses,photos",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    data = people_res.json()
    name = data.get("names", [{}])[0].get("displayName", "")
    email = data.get("emailAddresses", [{}])[0].get("value", "")
    account_id = data.get("resourceName", "").replace("people/", "")

    exist = await factory_reset_protection_service.get_factory_reset_protection_by_account(account_id)
    if not exist:
        factory = FactoryResetProtectionCreate(
            account_id = account_id,
            name = name,
            email = email,
            state = FactoryResetProtectionState.ACTIVE
        )
        await factory_reset_protection_service.create_factory_reset_protection(factory)

    query = urllib.parse.urlencode({
        "name": name,
        "email": email,
        "account_id": account_id
    })

    return RedirectResponse(f"http://localhost:5173/configuration/response?{query}")