# industries/crud.py
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas

def get_category_by_level(level: int) -> str:
    """Get category based on hierarchy level"""
    if level == 0:
        return "Main Industry"
    elif level == 1:
        return "sub"
    elif level == 2:
        return "sub-sub"
    elif level == 3:
        return "sub-sub-sub"
    else:
        category = "sub"
        for i in range(1, level):
            category += "-sub"
        return category

def get_industry_level(db: Session, industry_id: int) -> int:
    """Get the level of an industry in hierarchy"""
    industry = db.query(models.Industry).filter(models.Industry.id == industry_id).first()
    if not industry or industry.parent_id is None:
        return 0
    return get_industry_level(db, industry.parent_id) + 1

def update_industry_and_children_categories(db: Session, industry_id: int, new_level: int):
    """Update category of an industry and all its descendants"""
    industry = db.query(models.Industry).filter(models.Industry.id == industry_id).first()
    if industry:
        industry.category = get_category_by_level(new_level)
        children = db.query(models.Industry).filter(models.Industry.parent_id == industry_id).all()
        for child in children:
            update_industry_and_children_categories(db, child.id, new_level + 1)

def is_descendant(db: Session, child_id: int, parent_id: int, visited=None) -> bool:
    """Check if parent_id is a descendant of child_id"""
    if visited is None:
        visited = set()
    
    if child_id == parent_id:
        return True
    
    if child_id in visited:
        return False
    
    visited.add(child_id)
    
    children = db.query(models.Industry).filter(models.Industry.parent_id == child_id).all()
    for child in children:
        if is_descendant(db, child.id, parent_id, visited):
            return True
    
    return False

def get_all_children(parent_id: int, db: Session) -> List[models.Industry]:
    """Get all children recursively for an industry"""
    children = db.query(models.Industry).filter(models.Industry.parent_id == parent_id).all()
    all_children = list(children)
    for child in children:
        all_children.extend(get_all_children(child.id, db))
    return all_children

def get_industry(db: Session, industry_id: int) -> Optional[models.Industry]:
    """Get a single industry by ID"""
    return db.query(models.Industry).filter(models.Industry.id == industry_id).first()

def get_industries(db: Session, skip: int = 0, limit: int = 100) -> List[models.Industry]:
    """Get industries with pagination"""
    return db.query(models.Industry).offset(skip).limit(limit).all()

def get_all_industries(db: Session) -> List[models.Industry]:
    """Get all industries"""
    return db.query(models.Industry).all()

def create_industry(db: Session, industry: schemas.IndustryCreate) -> models.Industry:
    """Create a new industry"""
    industry_data = industry.dict()
    
    if industry_data.get('parent_id'):
        parent_level = get_industry_level(db, industry_data['parent_id'])
        industry_data['category'] = get_category_by_level(parent_level + 1)
    else:
        industry_data['category'] = "Main Industry"
    
    db_industry = models.Industry(**industry_data)
    db.add(db_industry)
    db.commit()
    db.refresh(db_industry)
    return db_industry

def update_industry_name(db: Session, industry_id: int, industry: schemas.IndustryNameUpdate) -> Optional[models.Industry]:
    """Update industry name"""
    db_industry = get_industry(db, industry_id)
    if db_industry:
        db_industry.industry_name = industry.industry_name
        db.commit()
        db.refresh(db_industry)
    return db_industry

def update_industry_parent(db: Session, update: schemas.IndustryUpdateParent) -> Optional[models.Industry]:
    """Update industry parent relationship"""
    industry = get_industry(db, update.id)
    if not industry:
        return None

    if update.new_parent_id is not None:
        parent = get_industry(db, update.new_parent_id)
        if not parent:
            return None
        if update.new_parent_id == update.id:
            return None
        if is_descendant(db, update.id, update.new_parent_id):
            return None

    industry.parent_id = update.new_parent_id
    
    if update.new_parent_id is None:
        new_level = 0
    else:
        parent_level = get_industry_level(db, update.new_parent_id)
        new_level = parent_level + 1
    
    update_industry_and_children_categories(db, update.id, new_level)
    
    db.commit()
    db.refresh(industry)
    return industry

def delete_industry(db: Session, industry_id: int) -> bool:
    """Delete industry and all its children"""
    industry = get_industry(db, industry_id)
    if not industry:
        return False
    
    children_to_delete = get_all_children(industry_id, db)
    
    for child in children_to_delete:
        db.delete(child)
    
    db.delete(industry)
    db.commit()
    return True

def get_industry_children(db: Session, industry_id: int) -> List[models.Industry]:
    """Get direct children of an industry"""
    return db.query(models.Industry).filter(models.Industry.parent_id == industry_id).all()

def get_industry_hierarchy(db: Session) -> List[models.Industry]:
    """Get all industries in a hierarchical structure (top-level parents first)"""
    return db.query(models.Industry).filter(models.Industry.parent_id.is_(None)).all()

def fix_existing_categories(db: Session):
    """Fix categories for all existing industries"""
    root_industries = db.query(models.Industry).filter(models.Industry.parent_id == None).all()
    
    for root in root_industries:
        update_industry_and_children_categories(db, root.id, 0)
    
    db.commit()