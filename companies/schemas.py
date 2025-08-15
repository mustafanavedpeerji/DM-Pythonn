# companies/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import date


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
    legal_name: Optional[str] = None
    other_names: Optional[str] = None
    
    # Business Operations
    imports: BusinessActivity = BusinessActivity.N
    exports: BusinessActivity = BusinessActivity.N
    manufacture: BusinessActivity = BusinessActivity.N
    distribution: BusinessActivity = BusinessActivity.N
    wholesale: BusinessActivity = BusinessActivity.N
    retail: BusinessActivity = BusinessActivity.N
    services: BusinessActivity = BusinessActivity.N
    online: BusinessActivity = BusinessActivity.N
    soft_products: BusinessActivity = BusinessActivity.N
    
    # Additional Company Details
    living_status: LivingStatus = LivingStatus.ACTIVE
    ownership_type: Optional[str] = None
    global_operations: GlobalOperations = GlobalOperations.LOCAL
    founding_year: Optional[str] = None
    established_date: Optional[date] = None
    company_size: int = 3
    ntn_no: Optional[str] = None
    
    # Industries
    selected_industries: Optional[List[int]] = None
    
    # Ratings (1-5 scale)
    financial_rating: int = 3
    operational_rating: int = 3
    compliance_rating: int = 3
    market_rating: int = 3
    innovation_rating: int = 3


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    company_group_print_name: Optional[str] = None
    company_group_data_type: Optional[CompanyType] = None
    parent_id: Optional[int] = None
    legal_name: Optional[str] = None
    other_names: Optional[str] = None
    
    # Business Operations
    imports: Optional[BusinessActivity] = None
    exports: Optional[BusinessActivity] = None
    manufacture: Optional[BusinessActivity] = None
    distribution: Optional[BusinessActivity] = None
    wholesale: Optional[BusinessActivity] = None
    retail: Optional[BusinessActivity] = None
    services: Optional[BusinessActivity] = None
    online: Optional[BusinessActivity] = None
    soft_products: Optional[BusinessActivity] = None
    
    # Additional Company Details
    living_status: Optional[LivingStatus] = None
    ownership_type: Optional[str] = None
    global_operations: Optional[GlobalOperations] = None
    founding_year: Optional[str] = None
    established_date: Optional[date] = None
    company_size: Optional[int] = None
    ntn_no: Optional[str] = None
    
    # Industries
    selected_industries: Optional[List[int]] = None
    
    # Ratings
    financial_rating: Optional[int] = None
    operational_rating: Optional[int] = None
    compliance_rating: Optional[int] = None
    market_rating: Optional[int] = None
    innovation_rating: Optional[int] = None


class Company(CompanyBase):
    record_id: int

    class Config:
        from_attributes = True


class CompanyWithChildren(Company):
    children: List['CompanyWithChildren'] = []

    class Config:
        from_attributes = True


# Update forward references
CompanyWithChildren.model_rebuild()