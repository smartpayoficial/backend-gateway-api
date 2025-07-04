from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict




class EnrolmentBase(BaseModel):
    pass


class EnrolmentCreate(EnrolmentBase):
    user_id: UUID
    vendor_id: UUID


class EnrolmentUpdate(BaseModel):

    pass


class Enrolment(EnrolmentBase):
    enrolment_id: UUID
    user_id: UUID
    vendor_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)



class EnrolmentDB(Enrolment):
    model_config = ConfigDict(from_attributes=True)
