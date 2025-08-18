# groups/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import datetime

class LivingStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive" 
    DORMANT = "Dormant"
    IN_PROCESS = "In Process"

class GroupBase(BaseModel):
    group_print_name: str
    parent_id: Optional[int] = None
    legal_name: str
    other_names: Optional[str] = None
    living_status: LivingStatus = LivingStatus.ACTIVE

class GroupCreate(GroupBase):
    pass

class GroupUpdate(BaseModel):
    group_print_name: Optional[str] = None
    parent_id: Optional[int] = None
    legal_name: Optional[str] = None
    other_names: Optional[str] = None
    living_status: Optional[LivingStatus] = None

class Group(GroupBase):
    record_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class GroupWithChildren(Group):
    children: List['GroupWithChildren'] = []

    class Config:
        from_attributes = True

# Update forward references
GroupWithChildren.model_rebuild()