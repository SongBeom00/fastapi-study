from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Annotated
from pydantic.dataclasses import dataclass


# ✅ Create
class BoardCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    content: str = Field(..., max_length=500)

# ✅ Update
class BoardUpdate(BaseModel):
    id: int
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    content: Optional[str] = Field(None, max_length=500)

# ✅
class BoardDelete(BaseModel):
    id: int

# ✅ Response
class BoardResponse(BaseModel):
    id: int
    title: str
    content: str
    created_by: int
    updated_by: int
    created_at: datetime
    updated_at: Optional[datetime]


@dataclass
class BoardData:
    id: int
    title: str
    content: str
    created_by: int
    updated_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    is_deleted: bool
