# emails/schemas.py
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums for dropdown options
class EmailType(str, Enum):
    BUSINESS = "business"
    PERSONAL = "personal"
    SUPPORT = "support"
    SALES = "sales"
    INFO = "info"
    ADMIN = "admin"
    OTHER = "other"

class AssociationType(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUPPORT = "support"
    BILLING = "billing"
    TECHNICAL = "technical"
    OTHER = "other"

class EmailStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"

# Department enum (same as persons)
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

# Email Directory Schemas
class EmailDirectoryBase(BaseModel):
    email_address: EmailStr
    email_type: Optional[EmailType] = None
    description: Optional[str] = None
    is_active: EmailStatus = EmailStatus.ACTIVE

    @field_validator('email_address')
    @classmethod
    def validate_email_address(cls, v):
        # Additional email validation if needed
        if v:
            v = v.lower().strip()
            if len(v) > 255:
                raise ValueError('Email address too long (max 255 characters)')
        return v

class EmailDirectoryCreate(EmailDirectoryBase):
    pass

class EmailDirectoryUpdate(BaseModel):
    email_address: Optional[EmailStr] = None
    email_type: Optional[EmailType] = None
    description: Optional[str] = None
    is_active: Optional[EmailStatus] = None

    @field_validator('email_address')
    @classmethod
    def validate_email_address(cls, v):
        if v:
            v = v.lower().strip()
            if len(v) > 255:
                raise ValueError('Email address too long (max 255 characters)')
        return v

class EmailDirectory(EmailDirectoryBase):
    email_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Email Association Schemas
class EmailAssociationBase(BaseModel):
    email_id: int
    company_id: Optional[int] = None
    department: Optional[Department] = None
    person_id: Optional[int] = None
    association_type: Optional[AssociationType] = None
    notes: Optional[str] = None

    @field_validator('company_id', 'person_id')
    @classmethod
    def validate_ids(cls, v):
        if v is not None and v <= 0:
            raise ValueError('ID must be positive integer')
        return v

class EmailAssociationCreate(EmailAssociationBase):
    # At least one association must be provided
    def __init__(self, **data):
        super().__init__(**data)
        if not any([self.company_id, self.person_id]):
            raise ValueError("At least one association (company_id or person_id) must be provided")

class EmailAssociationUpdate(BaseModel):
    company_id: Optional[int] = None
    department: Optional[Department] = None
    person_id: Optional[int] = None
    association_type: Optional[AssociationType] = None
    notes: Optional[str] = None

class EmailAssociation(EmailAssociationBase):
    association_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Combined schemas for complex operations
class EmailWithAssociations(EmailDirectory):
    associations: List[EmailAssociation] = []

class EmailAssociationWithDetails(EmailAssociation):
    email: EmailDirectory

# Request schemas for adding email with associations
class EmailCreateRequest(BaseModel):
    email: EmailDirectoryCreate
    associations: List[EmailAssociationCreate] = []

# Response schemas
class EmailCreateResponse(BaseModel):
    email: EmailDirectory
    associations: List[EmailAssociation] = []
    message: str