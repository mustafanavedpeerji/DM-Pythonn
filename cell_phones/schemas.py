# cell_phones/schemas.py
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Status enum
class PhoneStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"

# Department enum (same as emails)
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

# Cell Phone Directory Schemas
class CellPhoneDirectoryBase(BaseModel):
    phone_number: str
    description: Optional[str] = None
    is_active: PhoneStatus = PhoneStatus.ACTIVE

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        # Basic phone number validation
        if v:
            v = v.strip()
            if len(v) < 7 or len(v) > 20:
                raise ValueError('Phone number must be between 7 and 20 characters')
        return v

class CellPhoneDirectoryCreate(CellPhoneDirectoryBase):
    pass

class CellPhoneDirectoryUpdate(BaseModel):
    phone_number: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[PhoneStatus] = None

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        if v:
            v = v.strip()
            if len(v) < 7 or len(v) > 20:
                raise ValueError('Phone number must be between 7 and 20 characters')
        return v

class CellPhoneDirectory(CellPhoneDirectoryBase):
    phone_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Cell Phone Association Schemas
class CellPhoneAssociationBase(BaseModel):
    phone_id: int
    company_id: Optional[int] = None
    departments: Optional[List[Department]] = None
    person_id: Optional[int] = None

    @field_validator('company_id', 'person_id')
    @classmethod
    def validate_ids(cls, v):
        if v is not None and v <= 0:
            raise ValueError('ID must be positive integer')
        return v

class CellPhoneAssociationCreate(BaseModel):
    phone_id: Optional[int] = None  # Will be set during creation process
    company_id: Optional[int] = None
    departments: Optional[List[Department]] = None
    person_id: Optional[int] = None

    @field_validator('company_id', 'person_id')
    @classmethod
    def validate_ids(cls, v):
        if v is not None and v <= 0:
            raise ValueError('ID must be positive integer')
        return v

    # At least one association must be provided
    def __init__(self, **data):
        super().__init__(**data)
        if not any([self.company_id, self.person_id]):
            raise ValueError("At least one association (company_id or person_id) must be provided")

class CellPhoneAssociationUpdate(BaseModel):
    company_id: Optional[int] = None
    departments: Optional[List[Department]] = None
    person_id: Optional[int] = None

class CellPhoneAssociation(CellPhoneAssociationBase):
    association_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Combined schemas for complex operations
class CellPhoneWithAssociations(CellPhoneDirectory):
    associations: List[CellPhoneAssociation] = []

class CellPhoneAssociationWithDetails(CellPhoneAssociation):
    phone: CellPhoneDirectory

# Request schemas for adding phone with associations
class CellPhoneCreateRequest(BaseModel):
    phone: CellPhoneDirectoryCreate
    associations: List[CellPhoneAssociationCreate] = []

# Response schemas
class CellPhoneCreateResponse(BaseModel):
    phone: CellPhoneDirectory
    associations: List[CellPhoneAssociation] = []
    message: str