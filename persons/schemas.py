# persons/schemas.py
from pydantic import BaseModel, field_validator
from typing import Optional, List
from enum import Enum
from datetime import date

# Enums for dropdown options
class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"

class LivingStatus(str, Enum):
    ACTIVE = "Active"
    DEAD = "Dead"
    MISSING = "Missing"

class ProfessionalStatus(str, Enum):
    PROFESSIONAL = "Professional"
    RETIRED = "Retired"
    STUDENT = "Student"
    DISABLED = "Disabled"
    MISSING = "Missing"
    UNEMPLOYED = "Unemployed"

class Religion(str, Enum):
    ISLAM = "Islam"
    HINDU = "Hindu"
    CHRISTIAN = "Christian"
    PERSIAN = "Persian"
    SIKH = "Sikh"
    BUDDHIST = "Buddhist"
    OTHER = "Other"
    UNKNOWN = "Unknown"

class Community(str, Enum):
    DELHI = "Delhi"
    MEMON = "Memon"
    BOHRI = "Bohri"
    PUNJABI = "Punjabi"
    SINDHI = "Sindhi"
    BALOCH = "Baloch"
    PATHAN = "Pathan"
    UNKNOWN = "Unknown"
    OTHER = "Other"

class AgeBracket(str, Enum):
    TWENTY_THIRTY = "20-30"
    THIRTY_FORTY = "30-40"
    FORTY_FIFTY = "40-50"
    FIFTY_SIXTY = "50-60"
    SIXTY_SEVENTY = "60-70"
    SEVENTY_EIGHTY = "70-80"
    EIGHTY_NINETY = "80-90"

class Department(str, Enum):
    BOARD_MEMBER = "Board Member"
    MANAGEMENT_ALL = "Management All"
    MANAGEMENT_OPERATIONS = "Management Operations"
    MANAGEMENT_ADMINISTRATION = "Management Administration"
    ENGINEERING_DEPARTMENT = "Engineering Department"
    RESEARCH_DEVELOPMENT = "Research & Development"
    REGULATORY_LEGAL = "Regulatory & Legal"
    QUALITY_CONTROL = "Quality Control"
    HUMAN_RESOURCE = "Human Resource"
    TRAINING_DEVELOPMENT = "Training & Development"
    PURCHASE_PROCUREMENT = "Purchase & Procurement"
    LOGISTICS_DISTRIBUTION = "Logistics & Distribution"
    FINANCE_ACCOUNTS = "Finance & Accounts"
    AUDIT_DEPARTMENT = "Audit Department"
    INFORMATION_TECHNOLOGY = "Information Technology"
    CREATIVE_DEPARTMENT = "Creative Department"
    CUSTOMER_SUPPORT = "Customer Support"
    SALES_SUPPORT = "Sales & Support"
    MARKETING_SALES = "Marketing & Sales"
    MARKETING_PLANNING = "Marketing & Planning"
    MARKETING_DIGITAL = "Marketing & Digital"
    ECOMMERCE_DEPARTMENT = "eCommerce Department"
    PR_DEPARTMENT = "PR Department"
    EDITORIAL_DEPARTMENT = "Editorial Department"
    IMPORT_EXPORT = "Import Export"
    PROTOCOL_SECURITY = "Protocol & Security"
    EXAMINATION_DEPARTMENT = "Examination Department"
    ACADEMICS_DEPARTMENT = "Academics Department"
    ADMISSIONS_DEPARTMENT = "Admissions Department"

# Pakistani cities
PAKISTANI_CITIES = [
    "Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad", "Multan", "Hyderabad", 
    "Gujranwala", "Peshawar", "Quetta", "Sialkot", "Bahawalpur", "Sargodha", "Sukkur", 
    "Larkana", "Sheikhupura", "Mirpur Khas", "Rahim Yar Khan", "Gujrat", "Sahiwal", 
    "Okara", "Wah Cantonment", "Dera Ghazi Khan", "Mardan", "Kasur", "Mingora", 
    "Nawabshah", "Chiniot", "Kotri", "Khanpur", "Hafizabad", "Sadiqabad", "Jacobabad", 
    "Shikarpur", "Khanewal", "Jhang", "Attock", "Muzaffargarh", "Mandi Bahauddin"
]

class PersonBase(BaseModel):
    person_print_name: str
    full_name: str
    gender: Gender
    living_status: LivingStatus = LivingStatus.ACTIVE
    professional_status: Optional[ProfessionalStatus] = None
    religion: Optional[Religion] = None
    community: Optional[Community] = None
    base_city: Optional[str] = None
    attached_companies: Optional[List[int]] = None
    department: Optional[Department] = None
    designation: Optional[str] = None
    date_of_birth: Optional[date] = None
    age_bracket: Optional[AgeBracket] = None
    nic: Optional[str] = None
    
    @field_validator('base_city')
    @classmethod
    def validate_cities(cls, v):
        if v and v not in PAKISTANI_CITIES:
            # Allow custom cities but log a warning
            pass
        return v
    
    @field_validator('nic')
    @classmethod
    def validate_nic(cls, v):
        if v:
            # Remove any spaces or dashes
            cleaned_nic = v.replace('-', '').replace(' ', '')
            # Basic validation for Pakistani NIC format
            if len(cleaned_nic) not in [13, 15]:  # Old format 13 digits, new format 15
                raise ValueError('NIC must be 13 or 15 digits')
            if not cleaned_nic.isdigit():
                raise ValueError('NIC must contain only digits')
            return cleaned_nic
        return v

class PersonCreate(PersonBase):
    pass

class PersonUpdate(BaseModel):
    person_print_name: Optional[str] = None
    full_name: Optional[str] = None
    gender: Optional[Gender] = None
    living_status: Optional[LivingStatus] = None
    professional_status: Optional[ProfessionalStatus] = None
    religion: Optional[Religion] = None
    community: Optional[Community] = None
    base_city: Optional[str] = None
    attached_companies: Optional[List[int]] = None
    department: Optional[Department] = None
    designation: Optional[str] = None
    date_of_birth: Optional[date] = None
    age_bracket: Optional[AgeBracket] = None
    nic: Optional[str] = None
    
    @field_validator('base_city')
    @classmethod
    def validate_cities(cls, v):
        if v and v not in PAKISTANI_CITIES:
            pass
        return v
    
    @field_validator('nic')
    @classmethod
    def validate_nic(cls, v):
        if v:
            cleaned_nic = v.replace('-', '').replace(' ', '')
            if len(cleaned_nic) not in [13, 15]:
                raise ValueError('NIC must be 13 or 15 digits')
            if not cleaned_nic.isdigit():
                raise ValueError('NIC must contain only digits')
            return cleaned_nic
        return v

class Person(PersonBase):
    record_id: int

    class Config:
        from_attributes = True