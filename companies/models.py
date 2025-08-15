# companies/models.py - PRODUCTION VERSION with correct column names
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Text, Date, JSON
from sqlalchemy.orm import relationship
from database import Base  # Import Base from database.py

class Company(Base):
    __tablename__ = "companies"

    # Map Python attributes to actual database column names (PascalCase)
    record_id = Column("Record_ID", Integer, primary_key=True, index=True, autoincrement=True)
    company_group_print_name = Column("Company_Group_Print_Name", String(255), nullable=False)
    company_group_data_type = Column("Company_Group_Data_Type", Enum('Company', 'Group', 'Division'), nullable=False)
    parent_id = Column("Parent_ID", Integer, ForeignKey('companies.Record_ID', ondelete='CASCADE'), nullable=True)
    legal_name = Column("Legal_Name", String(255), nullable=False)
    other_names = Column("Other_Names", Text, nullable=True)
    
    # Business Operations
    imports = Column("Imports", Enum('Y', 'N'), default='N')
    exports = Column("Exports", Enum('Y', 'N'), default='N')
    manufacture = Column("Manufacture", Enum('Y', 'N'), default='N')
    distribution = Column("Distribution", Enum('Y', 'N'), default='N')
    wholesale = Column("Wholesale", Enum('Y', 'N'), default='N')
    retail = Column("Retail", Enum('Y', 'N'), default='N')
    services = Column("Services", Enum('Y', 'N'), default='N')
    online = Column("Online", Enum('Y', 'N'), default='N')
    soft_products = Column("Soft_Products", Enum('Y', 'N'), default='N')
    
    # Additional Company Details (these should be lowercase in database)
    living_status = Column("living_status", Enum('Active', 'Inactive', 'Dormant', 'In Process'), default='Active')
    ownership_type = Column("ownership_type", String(100), nullable=True)
    global_operations = Column("global_operations", Enum('Local', 'National', 'Multi National'), default='Local')
    founding_year = Column("founding_year", String(4), nullable=True)
    established_day = Column("established_day", String(2), nullable=True)
    established_month = Column("established_month", String(2), nullable=True)
    company_size = Column("company_size", Integer, nullable=True)
    ntn_no = Column("ntn_no", String(50), nullable=True)
    website = Column("website", String(255), nullable=True)
    
    # Industries (stored as JSON array of IDs)
    selected_industries = Column("selected_industries", Text, nullable=True)  # Use Text instead of JSON for compatibility
    
    # Rating Fields (1-5 scale) - User will enter, no defaults
    company_brand_image = Column("company_brand_image", Integer, nullable=True)
    company_business_volume = Column("company_business_volume", Integer, nullable=True)
    company_financials = Column("company_financials", Integer, nullable=True)
    iisol_relationship = Column("iisol_relationship", Integer, nullable=True)

    # Self-referencing relationship
    parent = relationship("Company", remote_side=[record_id], backref="children")