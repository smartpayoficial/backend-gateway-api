from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SimBase(BaseModel):
    device_id: UUID
    icc_id: str 
    slot_index: str
    operator: str 
    number: str 
    state: str


class SimCreate(SimBase):
    pass


class SimUpdate(BaseModel):
    device_id: Optional[UUID] = None
    slot_index: Optional[str] = None
    operator: Optional[str] = None
    number: Optional[str] = None
    state: Optional[str] = None


class SimInDBBase(SimBase):
    sim_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Sim(SimInDBBase):
    pass

