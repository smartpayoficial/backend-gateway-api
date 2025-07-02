from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.models.action import ActionCreate, ActionResponse, ActionState, ActionUpdate
from app.services import action as action_service

router = APIRouter()


@router.post("/", response_model=ActionResponse, status_code=status.HTTP_201_CREATED)
async def create_action(action: ActionCreate):
    """
    Creates a new action.
    """
    return await action_service.create_action(action)


@router.get("/{action_id}", response_model=ActionResponse)
async def get_action(action_id: UUID):
    """
    Retrieves a single action by its ID.
    """
    action = await action_service.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action


@router.get("/", response_model=List[ActionResponse])
async def get_actions(
    device_id: Optional[UUID] = Query(None),
    state: Optional[ActionState] = Query(None),
):
    """
    Retrieves a list of actions, with optional filters.
    """
    return await action_service.get_actions(device_id=device_id, state=state)


@router.patch("/{action_id}", response_model=ActionResponse)
async def update_action(action_id: UUID, action_update: ActionUpdate):
    """
    Updates an existing action.
    """
    updated_action = await action_service.update_action(action_id, action_update)
    if not updated_action:
        raise HTTPException(status_code=404, detail="Action not found")
    return updated_action


@router.delete("/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action(action_id: UUID):
    """
    Deletes an action.
    """
    deleted = await action_service.delete_action(action_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Action not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
