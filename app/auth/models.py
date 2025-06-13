from enum import Enum

from pydantic import BaseModel


class RoleName(str, Enum):
    admin = "admin"
    support = "support"
    user = "user"


class UserOut(BaseModel):
    user_id: str
    username: str
    is_active: bool
    role: RoleName
