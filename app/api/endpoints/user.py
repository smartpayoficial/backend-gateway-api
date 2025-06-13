import os

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

USER_SVC_URL = os.getenv("USER_SVC_URL") or os.getenv("DB_API", "http://localhost:8002")
USER_API_PREFIX = "/api/v1"
INTERNAL_HDR = {"X-Internal-Request": "true"}


class UserCreateIn(BaseModel):
    city_id: str
    dni: str = Field(..., max_length=15)
    first_name: str
    middle_name: str | None = None
    last_name: str
    second_last_name: str | None = None
    email: str
    prefix: str
    phone: str
    address: str
    username: str
    password: str
    role_id: str
    state: str = "Active"


class UserOut(BaseModel):
    user_id: str
    city: dict | None = None
    dni: str
    first_name: str
    middle_name: str | None = None
    last_name: str
    second_last_name: str | None = None
    email: str
    prefix: str
    phone: str
    address: str
    username: str
    state: str
    created_at: str | None = None
    updated_at: str | None = None


@router.post("/users", response_model=UserOut, status_code=201)
async def create_user(data: UserCreateIn):
    async with httpx.AsyncClient() as client:
        url = f"{USER_SVC_URL}{USER_API_PREFIX}/users"
        resp = await client.post(url, headers=INTERNAL_HDR, json=data.dict())
    if resp.status_code != 201:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()
