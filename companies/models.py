# companies/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Text, Date, JSON
from sqlalchemy.orm import relationship
from database import Base  # Import Base from database.py

class Company(Base):
    __tablename__ = "companies"  # Fixed: was 'tablename', should be '__tablename__'

    record_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_group_print_name = Column(String(255), nullable=False)
    company_group_data_type = Column(Enum('Company', 'Group', 'Division'), nullable=False)
    parent_id = Column(Integer, ForeignKey('companies.record_id', ondelete='CASCADE'), nullable=True)
    legal_name = Column(String(255), nullable=True)  # Changed from nullable=False to nullable=True
    other_names = Column(Text, nullable=True)
    
    # Business Operations
    imports = Column(Enum('Y', 'N'), default='N')
    exports = Column(Enum('Y', 'N'), default='N')
    manufacture = Column(Enum('Y', 'N'), default='N')
    distribution = Column(Enum('Y', 'N'), default='N')
    wholesale = Column(Enum('Y', 'N'), default='N')
    retail = Column(Enum('Y', 'N'), default='N')
    services = Column(Enum('Y', 'N'), default='N')
    online = Column(Enum('Y', 'N'), default='N')
    soft_products = Column(Enum('Y', 'N'), default='N')
    
    # Additional Company Details
    living_status = Column(Enum('Active', 'Inactive', 'Dormant', 'In Process'), default='Active')
    ownership_type = Column(String(100), nullable=True)  # Individual, Sole Proprietorship, etc.
    global_operations = Column(Enum('Local', 'National', 'Multi National'), default='Local')
    founding_year = Column(String(4), nullable=True)  # Store as string for flexibility
    established_date = Column(Date, nullable=True)
    company_size = Column(Integer, default=3)  # 1-5 scale
    ntn_no = Column(String(50), nullable=True)
    
    # Industries (stored as JSON array of IDs)
    selected_industries = Column(JSON, nullable=True)
    
    # Rating Fields (1-5 scale)
    financial_rating = Column(Integer, default=3)
    operational_rating = Column(Integer, default=3)
    compliance_rating = Column(Integer, default=3)
    market_rating = Column(Integer, default=3)
    innovation_rating = Column(Integer, default=3)

    # Self-referencing relationship
    parent = relationship("Company", remote_side=[record_id], backref="children")