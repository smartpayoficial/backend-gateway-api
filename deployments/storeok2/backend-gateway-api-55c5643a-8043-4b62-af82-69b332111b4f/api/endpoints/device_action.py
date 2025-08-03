from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from app.models.action import ActionType
from app.services.socket_service import send_and_log_action

router = APIRouter()


class ActionBody(BaseModel):
    applied_by_id: UUID
    payload: Optional[Dict[str, Any]] = None


@router.post("/{device_id}/block", tags=["Device Actions"])
async def action_block(device_id: UUID, body: ActionBody):
    """Block a device"""
    return await send_and_log_action(
        device_id, ActionType.BLOCK, body.applied_by_id, body.payload
    )


@router.post("/{device_id}/block_sim", tags=["Device Actions"])
async def action_block_sim(device_id: UUID, body: ActionBody):
    """Block a device SIM"""
    return await send_and_log_action(
        device_id, ActionType.BLOCK_SIM, body.applied_by_id, body.payload
    )


@router.post("/{device_id}/locate", tags=["Device Actions"])
async def action_locate(device_id: UUID, body: ActionBody):
    """Locate a device"""
    return await send_and_log_action(
        device_id, "locate", body.applied_by_id, body.payload
    )


@router.post("/{device_id}/refresh", tags=["Device Actions"])
async def action_refresh(device_id: UUID, body: ActionBody):
    """Refresh a device"""
    return await send_and_log_action(
        device_id, "refresh", body.applied_by_id, body.payload
    )


@router.post("/{device_id}/notify", tags=["Device Actions"])
async def action_notify(device_id: UUID, body: ActionBody):
    """Send a notification to a device"""
    return await send_and_log_action(
        device_id, "notify", body.applied_by_id, body.payload
    )


@router.post("/{device_id}/unenroll", tags=["Device Actions"])
async def action_unenroll(device_id: UUID, body: ActionBody):
    """Unenroll a device"""
    return await send_and_log_action(
        device_id, "unenroll", body.applied_by_id, body.payload
    )


@router.post("/{device_id}/unblock", tags=["Device Actions"])
async def action_unblock(device_id: UUID, body: ActionBody):
    """Unblock a device"""
    return await send_and_log_action(
        device_id, ActionType.UN_BLOCK, body.applied_by_id, body.payload
    )


@router.post("/{device_id}/unblock_sim", tags=["Device Actions"])
async def action_unblock_sim(device_id: UUID, body: ActionBody):
    """Unblock a device SIM"""
    return await send_and_log_action(
        device_id, "unblock_sim", body.applied_by_id, body.payload
    )


@router.post("/{device_id}/exception", tags=["Device Actions"])
async def action_exception(device_id: UUID, body: ActionBody):
    """Send an exception to a device"""
    return await send_and_log_action(
        device_id, "exception", body.applied_by_id, body.payload
    )
