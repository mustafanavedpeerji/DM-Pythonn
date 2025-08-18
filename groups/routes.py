# groups/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from . import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.Group)
def create_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
    """Create a new group"""
    try:
        print(f"🔍 BACKEND: Received group data: {group.dict()}")
        result = crud.create_group(db=db, group=group)
        print(f"🚀 BACKEND: Created group with ID: {result.record_id}")
        return result
    except Exception as e:
        print(f"❌ BACKEND: Error creating group: {e}")
        raise HTTPException(status_code=400, detail=f"Error creating group: {str(e)}")

@router.get("/", response_model=List[schemas.Group])
def read_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get groups with pagination"""
    groups = crud.get_groups(db, skip=skip, limit=limit)
    return groups

@router.get("/all", response_model=List[schemas.Group])
def read_all_groups(db: Session = Depends(get_db)):
    """Get all groups"""
    groups = crud.get_all_groups(db)
    return groups

@router.get("/tree", response_model=List[schemas.GroupWithChildren])
def get_group_tree(db: Session = Depends(get_db)):
    """Get group hierarchy tree"""
    try:
        top_level_groups = crud.get_group_hierarchy(db)

        def build_tree(group):
            children = crud.get_group_children(db, group.record_id)
            return {
                **schemas.Group.from_orm(group).dict(),
                "children": [build_tree(child) for child in children]
            }

        return [build_tree(group) for group in top_level_groups]
    except Exception as e:
        print(f"Error getting group tree: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting group tree: {str(e)}")

@router.get("/search", response_model=List[schemas.Group])
def search_groups(q: str = Query(..., description="Search term"), db: Session = Depends(get_db)):
    """Search groups by name"""
    if len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Search term must be at least 2 characters")

    groups = crud.search_groups(db, q)
    return groups

@router.get("/{group_id}", response_model=schemas.Group)
def read_group(group_id: int, db: Session = Depends(get_db)):
    """Get a specific group by ID"""
    db_group = crud.get_group(db, record_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return db_group

@router.put("/{group_id}", response_model=schemas.Group)
def update_group(group_id: int, group: schemas.GroupUpdate, db: Session = Depends(get_db)):
    """Update a group"""
    try:
        db_group = crud.update_group(db, group_id, group)
        if db_group is None:
            raise HTTPException(status_code=404, detail="Group not found")
        return db_group
    except Exception as e:
        print(f"Error updating group: {e}")
        raise HTTPException(status_code=400, detail=f"Error updating group: {str(e)}")

@router.delete("/{group_id}")
def delete_group(group_id: int, db: Session = Depends(get_db)):
    """Delete a group and all its children"""
    success = crud.delete_group(db, group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"message": "Group and its children deleted successfully"}

@router.post("/update-parent", response_model=schemas.Group)
def update_group_parent(
    group_id: int,
    new_parent_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Update a group's parent relationship"""
    db_group = crud.update_group_parent(db, group_id, new_parent_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found or invalid parent ID")
    return db_group