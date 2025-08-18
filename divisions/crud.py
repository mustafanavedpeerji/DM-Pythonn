# divisions/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from . import models, schemas

def get_division(db: Session, record_id: int) -> Optional[models.Division]:
    """Get a single division by ID"""
    return db.query(models.Division).filter(models.Division.record_id == record_id).first()

def get_divisions(db: Session, skip: int = 0, limit: int = 100) -> List[models.Division]:
    """Get divisions with pagination"""
    return db.query(models.Division).offset(skip).limit(limit).all()

def get_all_divisions(db: Session) -> List[models.Division]:
    """Get all divisions"""
    return db.query(models.Division).all()

def create_division(db: Session, division: schemas.DivisionCreate) -> models.Division:
    """Create a new division"""
    division_dict = division.dict()
    
    # Automatically convert 0 → None for top-level divisions
    if division_dict.get("parent_id") == 0:
        division_dict["parent_id"] = None
    
    # Handle empty strings for optional fields
    if division_dict.get("other_names") == "":
        division_dict["other_names"] = None

    db_division = models.Division(**division_dict)
    db.add(db_division)
    db.commit()
    db.refresh(db_division)
    return db_division

def update_division(db: Session, record_id: int, division: schemas.DivisionUpdate) -> Optional[models.Division]:
    """Update an existing division"""
    db_division = get_division(db, record_id)
    if db_division:
        update_data = division.dict(exclude_unset=True)
        
        # Handle empty strings for optional fields
        if update_data.get("other_names") == "":
            update_data["other_names"] = None
            
        for field, value in update_data.items():
            setattr(db_division, field, value)
        db.commit()
        db.refresh(db_division)
    return db_division

def delete_division(db: Session, record_id: int) -> bool:
    """Delete a division"""
    db_division = get_division(db, record_id)
    if db_division:
        db.delete(db_division)
        db.commit()
        return True
    return False

def search_divisions(db: Session, search_term: str) -> List[models.Division]:
    """Search divisions by name or legal name"""
    search_pattern = f"%{search_term}%"
    return db.query(models.Division).filter(
        or_(
            models.Division.division_print_name.ilike(search_pattern),
            models.Division.legal_name.ilike(search_pattern),
            models.Division.other_names.ilike(search_pattern)
        )
    ).all()

def get_divisions_by_parent(db: Session, parent_id: int, parent_type: str) -> List[models.Division]:
    """Get divisions by parent (group or division)"""
    return db.query(models.Division).filter(
        models.Division.parent_id == parent_id,
        models.Division.parent_type == parent_type
    ).all()

def update_division_parent(db: Session, division_id: int, new_parent_id: Optional[int], parent_type: Optional[str]) -> Optional[models.Division]:
    """Update a division's parent relationship"""
    db_division = get_division(db, division_id)
    if db_division:
        db_division.parent_id = new_parent_id
        db_division.parent_type = parent_type
        db.commit()
        db.refresh(db_division)
    return db_division