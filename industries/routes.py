# industries/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from . import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.Industry)
def create_industry(industry: schemas.IndustryCreate, db: Session = Depends(get_db)):
    """Create a new industry"""
    try:
        return crud.create_industry(db=db, industry=industry)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating industry: {str(e)}")

@router.get("/", response_model=List[schemas.Industry])
def read_industries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get industries with pagination"""
    try:
        industries = crud.get_industries(db, skip=skip, limit=limit)
        return industries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching industries: {str(e)}")

@router.get("/all", response_model=List[schemas.Industry])
def read_all_industries(db: Session = Depends(get_db)):
    """Get all industries"""
    try:
        return crud.get_all_industries(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching industries: {str(e)}")

@router.get("/tree")
def get_industry_tree(db: Session = Depends(get_db)):
    """Get industry hierarchy tree"""
    try:
        all_industries = crud.get_all_industries(db)
        
        industry_map = {ind.id: {
            "id": ind.id,
            "industry_name": ind.industry_name,
            "category": ind.category,
            "parent_id": ind.parent_id,
            "children": []
        } for ind in all_industries}
        
        tree = []
        for industry in all_industries:
            if industry.parent_id is None:
                tree.append(industry_map[industry.id])
            else:
                if industry.parent_id in industry_map:
                    industry_map[industry.parent_id]["children"].append(industry_map[industry.id])
        
        return tree
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building tree: {str(e)}")

@router.get("/{industry_id}", response_model=schemas.Industry)
def read_industry(industry_id: int, db: Session = Depends(get_db)):
    """Get a specific industry by ID"""
    try:
        db_industry = crud.get_industry(db, industry_id=industry_id)
        if db_industry is None:
            raise HTTPException(status_code=404, detail="Industry not found")
        return db_industry
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching industry: {str(e)}")

@router.get("/{industry_id}/children", response_model=List[schemas.Industry])
def read_industry_children(industry_id: int, db: Session = Depends(get_db)):
    """Get direct children of an industry"""
    try:
        children = crud.get_industry_children(db, industry_id)
        return children
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching children: {str(e)}")

@router.put("/{industry_id}", response_model=schemas.Industry)
def update_industry(industry_id: int, industry: schemas.IndustryNameUpdate, db: Session = Depends(get_db)):
    """Update industry name"""
    try:
        db_industry = crud.update_industry_name(db, industry_id, industry)
        if db_industry is None:
            raise HTTPException(status_code=404, detail="Industry not found")
        return db_industry
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating industry: {str(e)}")

@router.post("/update-parent")
def update_industry_parent(update: schemas.IndustryUpdateParent, db: Session = Depends(get_db)):
    """Update industry parent relationship"""
    try:
        db_industry = crud.update_industry_parent(db, update)
        if db_industry is None:
            raise HTTPException(status_code=404, detail="Industry not found or invalid parent ID")
        return {"message": "Parent updated successfully", "industry": db_industry}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating parent: {str(e)}")

@router.delete("/{industry_id}")
def delete_industry(industry_id: int, db: Session = Depends(get_db)):
    """Delete industry and all its children"""
    try:
        # Get count of children before deletion
        children_to_delete = crud.get_all_children(industry_id, db)
        children_count = len(children_to_delete)
        
        success = crud.delete_industry(db, industry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Industry not found")
        
        return {
            "message": f"Industry and {children_count} children deleted successfully",
            "deleted_count": children_count + 1
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting industry: {str(e)}")

@router.post("/fix-categories")
def fix_existing_categories(db: Session = Depends(get_db)):
    """Fix categories for all existing industries"""
    try:
        crud.fix_existing_categories(db)
        return {"message": "Categories fixed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fixing categories: {str(e)}")