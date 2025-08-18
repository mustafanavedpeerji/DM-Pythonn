# divisions/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from . import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.Division)
def create_division(division: schemas.DivisionCreate, db: Session = Depends(get_db)):
    """Create a new division"""
    try:
        print(f"🔍 BACKEND: Received division data: {division.dict()}")
        result = crud.create_division(db=db, division=division)
        print(f"🚀 BACKEND: Created division with ID: {result.record_id}")
        return result
    except Exception as e:
        print(f"❌ BACKEND: Error creating division: {e}")
        raise HTTPException(status_code=400, detail=f"Error creating division: {str(e)}")

@router.get("/", response_model=List[schemas.Division])
def read_divisions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get divisions with pagination"""
    divisions = crud.get_divisions(db, skip=skip, limit=limit)
    return divisions

@router.get("/all", response_model=List[schemas.Division])
def read_all_divisions(db: Session = Depends(get_db)):
    """Get all divisions"""
    divisions = crud.get_all_divisions(db)
    return divisions

@router.get("/search", response_model=List[schemas.Division])
def search_divisions(q: str = Query(..., description="Search term"), db: Session = Depends(get_db)):
    """Search divisions by name"""
    if len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Search term must be at least 2 characters")

    divisions = crud.search_divisions(db, q)
    return divisions

@router.get("/by-parent", response_model=List[schemas.Division])
def get_divisions_by_parent(parent_id: int, parent_type: str, db: Session = Depends(get_db)):
    """Get divisions by parent (group or division)"""
    valid_types = ["Group", "Division"]
    if parent_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid parent type. Must be one of: {valid_types}")

    divisions = crud.get_divisions_by_parent(db, parent_id, parent_type)
    return divisions

@router.get("/{division_id}", response_model=schemas.Division)
def read_division(division_id: int, db: Session = Depends(get_db)):
    """Get a specific division by ID"""
    db_division = crud.get_division(db, record_id=division_id)
    if db_division is None:
        raise HTTPException(status_code=404, detail="Division not found")
    return db_division

@router.put("/{division_id}", response_model=schemas.Division)
def update_division(division_id: int, division: schemas.DivisionUpdate, db: Session = Depends(get_db)):
    """Update a division"""
    try:
        db_division = crud.update_division(db, division_id, division)
        if db_division is None:
            raise HTTPException(status_code=404, detail="Division not found")
        return db_division
    except Exception as e:
        print(f"Error updating division: {e}")
        raise HTTPException(status_code=400, detail=f"Error updating division: {str(e)}")

@router.delete("/{division_id}")
def delete_division(division_id: int, db: Session = Depends(get_db)):
    """Delete a division"""
    success = crud.delete_division(db, division_id)
    if not success:
        raise HTTPException(status_code=404, detail="Division not found")
    return {"message": "Division deleted successfully"}

@router.post("/update-parent", response_model=schemas.Division)
def update_division_parent(
    division_id: int,
    new_parent_id: Optional[int] = None,
    parent_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update a division's parent relationship"""
    db_division = crud.update_division_parent(db, division_id, new_parent_id, parent_type)
    if db_division is None:
        raise HTTPException(status_code=404, detail="Division not found")
    return db_division