from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class IndustryBase(BaseModel):
    industry_name: str
    category: str
    parent_id: Optional[int] = None

class IndustryCreate(IndustryBase):
    pass

class IndustryUpdateParent(BaseModel):
    id: int
    new_parent_id: Optional[int] = None

class IndustryNameUpdate(BaseModel):
    industry_name: str

class Industry(IndustryBase):
    id: int

    class Config:
        from_attributes = True

