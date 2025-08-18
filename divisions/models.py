# divisions/models.py
from sqlalchemy import Column, Integer, String, Enum, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Division(Base):
    __tablename__ = "divisions"

    record_id = Column("Record_ID", Integer, primary_key=True, index=True, autoincrement=True)
    division_print_name = Column("Division_Print_Name", String(255), nullable=False)
    parent_id = Column("Parent_ID", Integer, nullable=True)  # References groups or divisions table
    parent_type = Column("Parent_Type", Enum('Group', 'Division'), nullable=True)
    legal_name = Column("Legal_Name", String(255), nullable=False)
    other_names = Column("Other_Names", Text, nullable=True)
    living_status = Column("Living_Status", Enum('Active', 'Inactive', 'Dormant', 'In Process'), default='Active')
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at = Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now())