from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .user import User


class EnrolmentBase(BaseModel):
    user_id: Optional[UUID] = None
    vendor_id: Optional[UUID] = None


class EnrolmentCreate(EnrolmentBase):
    pass


class EnrolmentUpdate(BaseModel):

    pass


class Enrolment(EnrolmentBase):
    enrolment_id: UUID
    user: User
    vendor: User
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EnrolmentDB(Enrolment):
    class Config:
        orm_mode = True
