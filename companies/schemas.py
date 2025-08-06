# companies/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class CompanyType(str, Enum):
    COMPANY = "Company"
    GROUP = "Group"
    DIVISION = "Division"


class BusinessActivity(str, Enum):
    Y = "Y"
    N = "N"


class CompanyBase(BaseModel):
    company_group_print_name: str
    company_group_data_type: CompanyType = CompanyType.COMPANY
    parent_id: Optional[int] = None
    legal_name: Optional[str] = None
    other_names: Optional[str] = None
    imports: BusinessActivity = BusinessActivity.N
    exports: BusinessActivity = BusinessActivity.N
    manufacture: BusinessActivity = BusinessActivity.N
    distribution: BusinessActivity = BusinessActivity.N
    wholesale: BusinessActivity = BusinessActivity.N
    retail: BusinessActivity = BusinessActivity.N
    services: BusinessActivity = BusinessActivity.N
    online: BusinessActivity = BusinessActivity.N
    soft_products: BusinessActivity = BusinessActivity.N


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    company_group_print_name: Optional[str] = None
    company_group_data_type: Optional[CompanyType] = None
    parent_id: Optional[int] = None
    legal_name: Optional[str] = None
    other_names: Optional[str] = None
    imports: Optional[BusinessActivity] = None
    exports: Optional[BusinessActivity] = None
    manufacture: Optional[BusinessActivity] = None
    distribution: Optional[BusinessActivity] = None
    wholesale: Optional[BusinessActivity] = None
    retail: Optional[BusinessActivity] = None
    services: Optional[BusinessActivity] = None
    online: Optional[BusinessActivity] = None
    soft_products: Optional[BusinessActivity] = None


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