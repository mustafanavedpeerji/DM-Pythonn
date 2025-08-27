# companies/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from . import models, schemas

def get_company(db: Session, record_id: int) -> Optional[models.Company]:
    """Get a single company by ID"""
    return db.query(models.Company).filter(models.Company.record_id == record_id).first()

def get_companies(db: Session, skip: int = 0, limit: int = 100) -> List[models.Company]:
    """Get companies with pagination"""
    return db.query(models.Company).offset(skip).limit(limit).all()

def get_all_companies(db: Session) -> List[models.Company]:
    """Get all companies"""
    return db.query(models.Company).all()

def create_company(db: Session, company: schemas.CompanyCreate) -> models.Company:
    """Create a new company"""
    # Convert the pydantic model to dict
    company_dict = company.dict()
    
    # Automatically convert 0 → None for top-level companies
    if company_dict.get("parent_id") == 0:
        company_dict["parent_id"] = None
    
    # Handle empty strings for optional fields
    if company_dict.get("legal_name") == "":
        company_dict["legal_name"] = None
    if company_dict.get("other_names") == "":
        company_dict["other_names"] = None
    
    # Convert operations object to comma-separated string
    operations_obj = company_dict.get("operations", {})
    if operations_obj and any(operations_obj.values()):  # Only if there are checked operations
        # Get only the True/checked operations
        selected_operations = [key for key, value in operations_obj.items() if value == True]
        company_dict["business_operations"] = ", ".join(selected_operations)
    else:
        company_dict["business_operations"] = None
    
    # Remove the operations key since it's not in the database model
    company_dict.pop("operations", None)

    db_company = models.Company(**company_dict)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def update_company(db: Session, record_id: int, company: schemas.CompanyUpdate) -> Optional[models.Company]:
    """Update an existing company"""
    db_company = get_company(db, record_id)
    if db_company:
        update_data = company.dict(exclude_unset=True)
        
        # Handle empty strings for optional fields
        if update_data.get("legal_name") == "":
            update_data["legal_name"] = None
        if update_data.get("other_names") == "":
            update_data["other_names"] = None
        
        # Convert operations object to comma-separated string
        operations_obj = update_data.get("operations")
        if operations_obj is not None:
            if operations_obj and any(operations_obj.values()):
                # Get only the True/checked operations
                selected_operations = [key for key, value in operations_obj.items() if value == True]
                update_data["business_operations"] = ", ".join(selected_operations)
            else:
                update_data["business_operations"] = None
            # Remove the operations key since it's not in the database model
            update_data.pop("operations", None)
            
        for field, value in update_data.items():
            setattr(db_company, field, value)
        db.commit()
        db.refresh(db_company)
    return db_company

def delete_company(db: Session, record_id: int) -> bool:
    """Delete a company and all its children"""
    db_company = get_company(db, record_id)
    if db_company:
        # First delete all children recursively
        children = db.query(models.Company).filter(models.Company.parent_id == record_id).all()
        for child in children:
            delete_company(db, child.record_id)

        # Then delete the company itself
        db.delete(db_company)
        db.commit()
        return True
    return False

def get_companies_by_type(db: Session, company_type: str) -> List[models.Company]:
    """Get companies filtered by type"""
    return db.query(models.Company).filter(
        models.Company.company_group_data_type == company_type
    ).all()

def search_companies(db: Session, search_term: str) -> List[models.Company]:
    """Search companies by name or legal name"""
    search_pattern = f"%{search_term}%"  # Fixed: was 'searchterm'
    return db.query(models.Company).filter(
        or_(
            models.Company.company_group_print_name.ilike(search_pattern),
            models.Company.legal_name.ilike(search_pattern),
            models.Company.other_names.ilike(search_pattern)
        )
    ).all()

def get_company_hierarchy(db: Session) -> List[models.Company]:
    """Get all companies in a hierarchical structure (top-level parents first)"""
    return db.query(models.Company).filter(models.Company.parent_id.is_(None)).all()  # Fixed: was 'parentid'

def get_company_children(db: Session, parent_id: int) -> List[models.Company]:
    """Get direct children of a company"""
    return db.query(models.Company).filter(models.Company.parent_id == parent_id).all()

def update_company_parent(db: Session, company_id: int, new_parent_id: Optional[int]) -> Optional[models.Company]:
    """Update a company's parent relationship"""
    db_company = get_company(db, company_id)
    if db_company:
        # Validate that new parent exists (if provided)
        if new_parent_id is not None:
            parent = get_company(db, new_parent_id)
            if not parent:
                return None

        db_company.parent_id = new_parent_id
        db.commit()
        db.refresh(db_company)
    return db_company