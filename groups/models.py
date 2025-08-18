# groups/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Group(Base):
    __tablename__ = "groups"

    record_id = Column("Record_ID", Integer, primary_key=True, index=True, autoincrement=True)
    group_print_name = Column("Group_Print_Name", String(255), nullable=False)
    parent_id = Column("Parent_ID", Integer, ForeignKey('groups.Record_ID', ondelete='CASCADE'), nullable=True)
    legal_name = Column("Legal_Name", String(255), nullable=False)
    other_names = Column("Other_Names", Text, nullable=True)
    living_status = Column("Living_Status", Enum('Active', 'Inactive', 'Dormant', 'In Process'), default='Active')
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at = Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Self-referencing relationship for group hierarchy
    parent = relationship("Group", remote_side=[record_id], backref="children")