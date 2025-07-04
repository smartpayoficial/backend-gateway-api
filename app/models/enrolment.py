from datetime import datetime

# Forward reference for User
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .user import User
else:
    User = Any


class EnrolmentBase(BaseModel):
    pass


class EnrolmentCreate(EnrolmentBase):
    user_id: UUID
    vendor_id: UUID


class EnrolmentUpdate(BaseModel):
    pass


class Enrolment(EnrolmentBase):
    enrolment_id: UUID
    user_id: Optional[UUID] = None
    vendor_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user: Optional[User] = None
    vendor: Optional[User] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",  # Ignore extra fields
        arbitrary_types_allowed=True,  # Allow arbitrary types
    )


class EnrolmentDB(Enrolment):
    model_config = ConfigDict(from_attributes=True)
