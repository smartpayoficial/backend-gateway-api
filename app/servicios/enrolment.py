import logging
import os
from typing import List, Optional
from uuid import UUID

import httpx
from fastapi import HTTPException

from app.models.enrolment import EnrolmentCreate, EnrolmentDB, EnrolmentUpdate
from app.servicios.user import get_user

DB_SVC_URL = os.getenv("USER_SVC_URL") or os.getenv("DB_API", "http://localhost:8002")
ENROLMENT_API_PREFIX = "/api/v1"
INTERNAL_HDR = {"X-Internal-Request": "true"}

# CRUD Functions for Enrolment entity


async def get_enrolment(enrolment_id: UUID) -> Optional[EnrolmentDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ENROLMENT_API_PREFIX}/enrolments/{enrolment_id}"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        enrolment_data = resp.json()
        if enrolment_data.get("user_id"):
            user_obj = await get_user(enrolment_data["user_id"])
            enrolment_data["user"] = user_obj.model_dump() if user_obj else None
        if enrolment_data.get("vendor_id"):
            vendor_obj = await get_user(enrolment_data["vendor_id"])
            enrolment_data["vendor"] = vendor_obj.model_dump() if vendor_obj else None
        return EnrolmentDB(**enrolment_data)
    return None


async def get_enrolments() -> List[EnrolmentDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ENROLMENT_API_PREFIX}/enrolments/"
        resp = await client.get(url, headers=INTERNAL_HDR)
    if resp.status_code == 200:
        enrolments_data = resp.json()
        enriched_enrolments = []
        for enrolment_data in enrolments_data:
            if enrolment_data.get("user_id"):
                user_obj = await get_user(enrolment_data["user_id"])
                enrolment_data["user"] = user_obj.model_dump() if user_obj else None
            if enrolment_data.get("vendor_id"):
                vendor_obj = await get_user(enrolment_data["vendor_id"])
                enrolment_data["vendor"] = (
                    vendor_obj.model_dump() if vendor_obj else None
                )
            enriched_enrolments.append(EnrolmentDB(**enrolment_data))
        return enriched_enrolments
    return []


async def create_enrolment(enrolment: EnrolmentCreate) -> EnrolmentDB:
    # Proactively validate that the user and vendor exist.
    user_obj = await get_user(enrolment.user_id)
    if not user_obj:
        raise HTTPException(
            status_code=400,
            detail=f"User with ID '{enrolment.user_id}' does not exist.",
        )

    vendor_obj = await get_user(enrolment.vendor_id)
    if not vendor_obj:
        raise HTTPException(
            status_code=400,
            detail=f"Vendor with ID '{enrolment.vendor_id}' does not exist.",
        )

    # If validation passes, proceed to create the enrolment.
    payload = enrolment.model_dump(mode="json")
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ENROLMENT_API_PREFIX}/enrolments/"
        try:
            resp = await client.post(url, headers=INTERNAL_HDR, json=payload)
            resp.raise_for_status()

            # Enrich the response with the objects we've already fetched.
            response_data = resp.json()
            response_data["user"] = user_obj.model_dump()
            response_data["vendor"] = vendor_obj.model_dump()

            return EnrolmentDB(**response_data)

        except httpx.HTTPStatusError as e:
            # Log unexpected errors from the downstream service.
            logging.error(
                f"Error creating enrolment. Downstream service responded with {e.response.status_code}."
            )
            logging.error(f"Response body: {e.response.text}")
            raise


async def update_enrolment(
    enrolment_id: UUID, enrolment: EnrolmentUpdate
) -> Optional[EnrolmentDB]:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ENROLMENT_API_PREFIX}/enrolments/{enrolment_id}"
        resp = await client.patch(
            url, headers=INTERNAL_HDR, json=enrolment.dict(exclude_none=True)
        )
    if resp.status_code == 204:
        return None
    resp.raise_for_status()
    return EnrolmentDB(**resp.json())


async def delete_enrolment(enrolment_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        url = f"{DB_SVC_URL}{ENROLMENT_API_PREFIX}/enrolments/{enrolment_id}"
        resp = await client.delete(url, headers=INTERNAL_HDR)
    return resp.status_code == 204
