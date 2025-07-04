from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .user import User


class ActionState(str, Enum):
    APPLIED = "applied"
    PENDING = "pending"
    FAILED = "failed"


class ActionType(str, Enum):
    BLOCK = "block"
    LOCATE = "locate"
    REFRESH = "refresh"
    NOTIFY = "notify"
    UN_ENROLL = "unenroll"
    UN_BLOCK = "unblock"
    EXCEPTION = "exception"
    BLOCK_SIM = "block_sim"
    UNBLOCK_SIM = "unblock_sim"


class ActionBase(BaseModel):
    device_id: UUID
    state: ActionState = ActionState.PENDING
    applied_by_id: UUID
    action: ActionType
    description: Optional[str] = None

    model_config = ConfigDict(
        json_encoders={
            UUID: str
        }
    )


class ActionCreate(ActionBase):
    pass


class ActionUpdate(BaseModel):
    state: Optional[ActionState] = None
    description: Optional[str] = None


class ActionInDB(ActionBase):
    action_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActionResponse(BaseModel):
    action_id: UUID
    device_id: UUID
    state: ActionState
    action: ActionType
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    applied_by: User

    model_config = ConfigDict(from_attributes=True)
