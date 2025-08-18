# divisions/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import datetime

class LivingStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive" 
    DORMANT = "Dormant"
    IN_PROCESS = "In Process"

class ParentType(str, Enum):
    GROUP = "Group"
    DIVISION = "Division"

class DivisionBase(BaseModel):
    division_print_name: str
    parent_id: Optional[int] = None
    parent_type: Optional[ParentType] = None
    legal_name: str
    other_names: Optional[str] = None
    living_status: LivingStatus = LivingStatus.ACTIVE

class DivisionCreate(DivisionBase):
    pass

class DivisionUpdate(BaseModel):
    division_print_name: Optional[str] = None
    parent_id: Optional[int] = None
    parent_type: Optional[ParentType] = None
    legal_name: Optional[str] = None
    other_names: Optional[str] = None
    living_status: Optional[LivingStatus] = None

class Division(DivisionBase):
    record_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DivisionWithChildren(Division):
    children: List['DivisionWithChildren'] = []

    class Config:
        from_attributes = True

# Update forward references
DivisionWithChildren.model_rebuild()