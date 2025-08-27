from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal

class AuditLogBase(BaseModel):
    table_name: str
    record_id: str
    field_name: str
    action_type: Literal['CREATE', 'UPDATE', 'DELETE']
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogResponse(AuditLogBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class AuditLogBatch(BaseModel):
    logs: list[AuditLogCreate]