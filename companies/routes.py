# companies/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from . import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.Company)
def create_company(company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    """Create a new company"""
    try:
        print(f"🔍 BACKEND: Received company data: {company.dict()}")
        print(f"🔍 BACKEND: Company ratings: brand_image={getattr(company, 'company_brand_image', None)}, business_volume={getattr(company, 'company_business_volume', None)}")
        print(f"🔍 BACKEND: Selected industries: {company.selected_industries}")
        print(f"🔍 BACKEND: Ownership type: {company.ownership_type}")
        
        result = crud.create_company(db=db, company=company)
        print(f"🚀 BACKEND: Created company with ID: {result.record_id}")
        return result
    except Exception as e:
        print(f"❌ BACKEND: Error creating company: {e}")  # Add logging
        raise HTTPException(status_code=400, detail=f"Error creating company: {str(e)}")

@router.get("/", response_model=List[schemas.Company])
def read_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get companies with pagination"""
    companies = crud.get_companies(db, skip=skip, limit=limit)
    return companies

@router.get("/all", response_model=List[schemas.Company])
def read_all_companies(db: Session = Depends(get_db)):
    """Get all companies"""
    companies = crud.get_all_companies(db)
    return companies

@router.get("/tree", response_model=List[schemas.CompanyWithChildren])
def get_company_tree(db: Session = Depends(get_db)):
    """Get company hierarchy tree"""
    try:
        top_level_companies = crud.get_company_hierarchy(db)

        def build_tree(company):
            children = crud.get_company_children(db, company.record_id)
            return {
                **schemas.Company.from_orm(company).dict(),
                "children": [build_tree(child) for child in children]
            }

        return [build_tree(company) for company in top_level_companies]
    except Exception as e:
        print(f"Error getting company tree: {e}")  # Add logging
        raise HTTPException(status_code=500, detail=f"Error getting company tree: {str(e)}")

@router.get("/search", response_model=List[schemas.Company])
def search_companies(q: str = Query(..., description="Search term"), db: Session = Depends(get_db)):
    """Search companies by name"""
    if len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Search term must be at least 2 characters")

    companies = crud.search_companies(db, q)
    return companies

@router.get("/by-type/{company_type}", response_model=List[schemas.Company])
def get_companies_by_type(company_type: str, db: Session = Depends(get_db)):
    """Get companies filtered by type"""
    valid_types = ["Company", "Group", "Division"]
    if company_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid company type. Must be one of: {valid_types}")

    companies = crud.get_companies_by_type(db, company_type)
    return companies

@router.get("/{company_id}", response_model=schemas.Company)
def read_company(company_id: int, db: Session = Depends(get_db)):
    """Get a specific company by ID"""
    db_company = crud.get_company(db, record_id=company_id)  # Fixed: parameter name should be 'record_id'
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company

@router.put("/{company_id}", response_model=schemas.Company)
def update_company(company_id: int, company: schemas.CompanyUpdate, db: Session = Depends(get_db)):
    """Update a company"""
    try:
        db_company = crud.update_company(db, company_id, company)
        if db_company is None:
            raise HTTPException(status_code=404, detail="Company not found")
        return db_company
    except Exception as e:
        print(f"Error updating company: {e}")  # Add logging
        raise HTTPException(status_code=400, detail=f"Error updating company: {str(e)}")

@router.delete("/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db)):
    """Delete a company and all its children"""
    success = crud.delete_company(db, company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"message": "Company and its children deleted successfully"}

@router.post("/update-parent", response_model=schemas.Company)
def update_company_parent(
    company_id: int,
    new_parent_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Update a company's parent relationship"""
    db_company = crud.update_company_parent(db, company_id, new_parent_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found or invalid parent ID")
    return db_company