# emails/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class EmailDirectory(Base):
    """Main email directory table - stores unique email addresses"""
    __tablename__ = "email_directory"

    # Primary key
    email_id = Column("email_id", Integer, primary_key=True, index=True, autoincrement=True)
    
    # Email information
    email_address = Column("email_address", String(255), nullable=False, unique=True, index=True)
    
    # Timestamps
    created_at = Column("created_at", DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Optional metadata
    email_type = Column("email_type", String(50), nullable=True)  # business, personal, support, etc.
    description = Column("description", Text, nullable=True)
    is_active = Column("is_active", String(10), default="Active")  # Active, Inactive
    gender = Column("gender", String(10), nullable=True)  # Male, Female, Unknown
    city = Column("city", String(100), nullable=True)  # City in Pakistan
    
    # Relationship to email associations
    associations = relationship("EmailAssociation", back_populates="email", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<EmailDirectory(email_id={self.email_id}, email_address='{self.email_address}')>"


class EmailAssociation(Base):
    """Email association table - links emails to companies, departments, and persons"""
    __tablename__ = "email_associations"

    # Primary key
    association_id = Column("association_id", Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to email directory
    email_id = Column("email_id", Integer, ForeignKey("email_directory.email_id"), nullable=False, index=True)
    
    # Association targets (all optional - at least one should be provided)
    company_id = Column("company_id", Integer, nullable=True, index=True)  # References companies table
    departments = Column("departments", JSON, nullable=True)  # List of department names
    person_id = Column("person_id", Integer, nullable=True, index=True)  # References persons table
    
    # Association metadata
    created_at = Column("created_at", DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship back to email directory
    email = relationship("EmailDirectory", back_populates="associations")

    def __repr__(self):
        return f"<EmailAssociation(association_id={self.association_id}, email_id={self.email_id}, company_id={self.company_id}, person_id={self.person_id})>"