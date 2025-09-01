# persons/models.py
from sqlalchemy import Column, Integer, String, Date, Enum, Text, JSON
from database import Base

class Person(Base):
    __tablename__ = "persons"

    # Primary key
    record_id = Column("Record_ID", Integer, primary_key=True, index=True, autoincrement=True)
    
    # Basic Information
    person_print_name = Column("person_print_name", String(255), nullable=False)
    full_name = Column("full_name", String(255), nullable=False)
    
    # Demographics
    gender = Column("gender", Enum('Male', 'Female'), nullable=False)
    living_status = Column("living_status", Enum('Active', 'Dead', 'Missing'), default='Active')
    professional_status = Column("professional_status", Enum(
        'Professional', 'Retired', 'Student', 'Disabled', 'Missing', 'Unemployed'
    ), nullable=True)
    
    # Cultural/Religious Information
    religion = Column("religion", Enum(
        'Islam', 'Hindu', 'Christian', 'Persian', 'Sikh', 'Buddhist', 'Other', 'Unknown'
    ), nullable=True)
    community = Column("community", Enum(
        'Delhi', 'Memon', 'Bohri', 'Punjabi', 'Sindhi', 'Baloch', 'Pathan', 'Unknown', 'Other'
    ), nullable=True)
    
    # Location Information
    base_city = Column("base_city", String(100), nullable=True)
    
    # Company and Professional Information
    attached_companies = Column("attached_companies", JSON, nullable=True)  # List of company IDs
    department = Column("department", String(100), nullable=True)
    designation = Column("designation", String(100), nullable=True)
    
    # Age Information
    date_of_birth = Column("date_of_birth", Date, nullable=True)
    age_bracket = Column("age_bracket", Enum(
        'Child (0-12)', 'Teen (13-19)', 'Young Adult (20-30)', 
        'Adult (31-50)', 'Middle Age (51-65)', 'Senior (65+)'
    ), nullable=True)
    
    # Identification
    nic = Column("nic", String(20), nullable=True, unique=True)
    
    def __repr__(self):
        return f"<Person(record_id={self.record_id}, person_print_name='{self.person_print_name}')>"