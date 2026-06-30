from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ✅ Response
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    tier: Optional[str] = None
    created_at: Optional[datetime] = None


# ✅ Update
class UserProfileUpdate(BaseModel):
    name: str
    email: str
    tier: str
