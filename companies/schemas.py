# companies/schemas.py
from pydantic import BaseModel, field_validator
from typing import Optional, List, Union
from enum import Enum
from datetime import date
import json


class CompanyType(str, Enum):
    COMPANY = "Company"
    GROUP = "Group"
    DIVISION = "Division"


class BusinessActivity(str, Enum):
    Y = "Y"
    N = "N"


class LivingStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive" 
    DORMANT = "Dormant"
    IN_PROCESS = "In Process"


class GlobalOperations(str, Enum):
    LOCAL = "Local"
    NATIONAL = "National"
    MULTI_NATIONAL = "Multi National"


class CompanyBase(BaseModel):
    company_group_print_name: str
    company_group_data_type: CompanyType = CompanyType.COMPANY
    parent_id: Optional[int] = None
    legal_name: str
    other_names: Optional[str] = None
    
    # Business Operations - Frontend sends object, backend stores as comma-separated string
    operations: Optional[dict] = None
    business_operations: Optional[str] = None
    
    # Additional Company Details
    living_status: LivingStatus = LivingStatus.ACTIVE
    ownership_type: Optional[str] = None
    global_operations: Optional[GlobalOperations] = None
    founding_year: Optional[str] = None
    established_day: Optional[str] = None
    established_month: Optional[str] = None
    company_size: Optional[int] = None
    ntn_no: Optional[str] = None
    websites: Optional[List[str]] = None
    
    # Industries
    selected_industries: Optional[Union[List[int], str]] = None
    
    @field_validator('selected_industries')
    @classmethod
    def convert_industries_to_json(cls, v):
        if v is None:
            return None
        if isinstance(v, list):
            return json.dumps(v)
        return v
    
    # Ratings (1-5 scale) - User will enter, default to None
    company_brand_image: Optional[int] = None
    company_business_volume: Optional[int] = None
    company_financials: Optional[int] = None
    iisol_relationship: Optional[int] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    company_group_print_name: Optional[str] = None
    company_group_data_type: Optional[CompanyType] = None
    parent_id: Optional[int] = None
    legal_name: Optional[str] = None
    other_names: Optional[str] = None
    
    # Business Operations
    operations: Optional[dict] = None
    business_operations: Optional[str] = None
    
    # Additional Company Details
    living_status: Optional[LivingStatus] = None
    ownership_type: Optional[str] = None
    global_operations: Optional[GlobalOperations] = None
    founding_year: Optional[str] = None
    established_day: Optional[str] = None
    established_month: Optional[str] = None
    company_size: Optional[int] = None
    ntn_no: Optional[str] = None
    websites: Optional[List[str]] = None
    
    # Industries
    selected_industries: Optional[Union[List[int], str]] = None
    
    # Ratings
    company_brand_image: Optional[int] = None
    company_business_volume: Optional[int] = None
    company_financials: Optional[int] = None
    iisol_relationship: Optional[int] = None


class Company(CompanyBase):
    record_id: int
    uid: str

    class Config:
        from_attributes = True


class CompanyWithChildren(Company):
    children: List['CompanyWithChildren'] = []

    class Config:
        from_attributes = True


# Update forward references
CompanyWithChildren.model_rebuild()