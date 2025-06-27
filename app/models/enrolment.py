from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from .user import User


class EnrolmentBase(BaseModel):
    pass


class EnrolmentCreate(EnrolmentBase):
    user_id: UUID
    vendor_id: UUID


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
