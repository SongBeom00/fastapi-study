from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Annotated
from pydantic.dataclasses import dataclass


class BoardInput(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    content: str = Field(..., max_length=500)


class Board(BoardInput):
    id: int
    created_by: int
    updated_by: int
    created_at: datetime
    updated_at: datetime


@dataclass
class BoardData:
    id: int
    title: str
    content: str
    created_by: int
    updated_by: int
    created_at: datetime
    updated_at: datetime
