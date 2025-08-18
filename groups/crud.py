# groups/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from . import models, schemas

def get_group(db: Session, record_id: int) -> Optional[models.Group]:
    """Get a single group by ID"""
    return db.query(models.Group).filter(models.Group.record_id == record_id).first()

def get_groups(db: Session, skip: int = 0, limit: int = 100) -> List[models.Group]:
    """Get groups with pagination"""
    return db.query(models.Group).offset(skip).limit(limit).all()

def get_all_groups(db: Session) -> List[models.Group]:
    """Get all groups"""
    return db.query(models.Group).all()

def create_group(db: Session, group: schemas.GroupCreate) -> models.Group:
    """Create a new group"""
    group_dict = group.dict()
    
    # Automatically convert 0 → None for top-level groups
    if group_dict.get("parent_id") == 0:
        group_dict["parent_id"] = None
    
    # Handle empty strings for optional fields
    if group_dict.get("other_names") == "":
        group_dict["other_names"] = None

    db_group = models.Group(**group_dict)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

def update_group(db: Session, record_id: int, group: schemas.GroupUpdate) -> Optional[models.Group]:
    """Update an existing group"""
    db_group = get_group(db, record_id)
    if db_group:
        update_data = group.dict(exclude_unset=True)
        
        # Handle empty strings for optional fields
        if update_data.get("other_names") == "":
            update_data["other_names"] = None
            
        for field, value in update_data.items():
            setattr(db_group, field, value)
        db.commit()
        db.refresh(db_group)
    return db_group

def delete_group(db: Session, record_id: int) -> bool:
    """Delete a group and all its children"""
    db_group = get_group(db, record_id)
    if db_group:
        # First delete all children recursively
        children = db.query(models.Group).filter(models.Group.parent_id == record_id).all()
        for child in children:
            delete_group(db, child.record_id)

        # Then delete the group itself
        db.delete(db_group)
        db.commit()
        return True
    return False

def search_groups(db: Session, search_term: str) -> List[models.Group]:
    """Search groups by name or legal name"""
    search_pattern = f"%{search_term}%"
    return db.query(models.Group).filter(
        or_(
            models.Group.group_print_name.ilike(search_pattern),
            models.Group.legal_name.ilike(search_pattern),
            models.Group.other_names.ilike(search_pattern)
        )
    ).all()

def get_group_hierarchy(db: Session) -> List[models.Group]:
    """Get all groups in a hierarchical structure (top-level parents first)"""
    return db.query(models.Group).filter(models.Group.parent_id.is_(None)).all()

def get_group_children(db: Session, parent_id: int) -> List[models.Group]:
    """Get direct children of a group"""
    return db.query(models.Group).filter(models.Group.parent_id == parent_id).all()

def update_group_parent(db: Session, group_id: int, new_parent_id: Optional[int]) -> Optional[models.Group]:
    """Update a group's parent relationship"""
    db_group = get_group(db, group_id)
    if db_group:
        # Validate that new parent exists (if provided)
        if new_parent_id is not None:
            parent = get_group(db, new_parent_id)
            if not parent:
                return None

        db_group.parent_id = new_parent_id
        db.commit()
        db.refresh(db_group)
    return db_group