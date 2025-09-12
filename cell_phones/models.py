# cell_phones/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class CellPhoneDirectory(Base):
    __tablename__ = "cell_phone_directory"

    phone_id = Column("phone_id", Integer, primary_key=True, index=True, autoincrement=True)
    phone_number = Column("phone_number", String(20), unique=True, nullable=False, index=True)
    description = Column("description", Text, nullable=True)
    is_active = Column("is_active", String(10), default="Active", nullable=False)
    created_at = Column("created_at", DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    # Relationships
    associations = relationship("CellPhoneAssociation", back_populates="phone", cascade="all, delete-orphan")


class CellPhoneAssociation(Base):
    __tablename__ = "cell_phone_associations"

    association_id = Column("association_id", Integer, primary_key=True, index=True, autoincrement=True)
    phone_id = Column("phone_id", Integer, ForeignKey("cell_phone_directory.phone_id"), nullable=False, index=True)
    company_id = Column("company_id", Integer, nullable=True, index=True)
    departments = Column("departments", JSON, nullable=True)  # List of department names
    person_id = Column("person_id", Integer, nullable=True, index=True)
    created_at = Column("created_at", DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    phone = relationship("CellPhoneDirectory", back_populates="associations")