from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column("id", Integer, primary_key=True, index=True, autoincrement=True)
    table_name = Column("table_name", String(100), nullable=False, index=True)
    record_id = Column("record_id", String(50), nullable=False, index=True)
    field_name = Column("field_name", String(100), nullable=False, index=True)
    action_type = Column("action_type", Enum('CREATE', 'UPDATE', 'DELETE'), nullable=False, index=True)
    old_value = Column("old_value", Text, nullable=True)
    new_value = Column("new_value", Text, nullable=True)
    user_id = Column("user_id", String(100), nullable=True)
    user_name = Column("user_name", String(255), nullable=True)
    timestamp = Column("timestamp", DateTime(timezone=True), nullable=False, default=func.now(), index=True)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, table={self.table_name}, record={self.record_id}, field={self.field_name}, action={self.action_type})>"