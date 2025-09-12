# cell_phones/crud.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from typing import List, Optional, Tuple
from . import models, schemas


def consolidate_associations(associations_data: List[schemas.CellPhoneAssociationCreate]) -> List[schemas.CellPhoneAssociationCreate]:
    """Consolidate associations with the same company+person combination by merging their departments"""
    consolidated = {}
    
    for assoc in associations_data:
        # Create a key based on company_id and person_id
        key = (assoc.company_id, assoc.person_id)
        
        if key in consolidated:
            # Merge departments
            existing = consolidated[key]
            existing_depts = existing.departments or []
            new_depts = assoc.departments or []
            
            # Combine and deduplicate departments
            combined_depts = list(set(existing_depts + new_depts))
            existing.departments = combined_depts if combined_depts else None
        else:
            consolidated[key] = assoc
    
    return list(consolidated.values())


# Cell Phone Directory CRUD
def get_phone(db: Session, phone_id: int) -> Optional[models.CellPhoneDirectory]:
    """Get a phone by ID"""
    return db.query(models.CellPhoneDirectory).filter(models.CellPhoneDirectory.phone_id == phone_id).first()


def get_phone_by_number(db: Session, phone_number: str) -> Optional[models.CellPhoneDirectory]:
    """Get a phone by phone number"""
    return db.query(models.CellPhoneDirectory).filter(models.CellPhoneDirectory.phone_number == phone_number).first()


def get_phones(db: Session, skip: int = 0, limit: int = 100) -> List[models.CellPhoneDirectory]:
    """Get phones with pagination"""
    return db.query(models.CellPhoneDirectory).offset(skip).limit(limit).all()


def get_all_phones(db: Session) -> List[models.CellPhoneDirectory]:
    """Get all phones"""
    return db.query(models.CellPhoneDirectory).all()


def search_phones(db: Session, search_term: str) -> List[models.CellPhoneDirectory]:
    """Search phones by number or description"""
    search_pattern = f"%{search_term}%"
    return db.query(models.CellPhoneDirectory).filter(
        or_(
            models.CellPhoneDirectory.phone_number.like(search_pattern),
            models.CellPhoneDirectory.description.like(search_pattern)
        )
    ).all()


def create_phone(db: Session, phone: schemas.CellPhoneDirectoryCreate) -> models.CellPhoneDirectory:
    """Create a new phone"""
    db_phone = models.CellPhoneDirectory(**phone.model_dump())
    db.add(db_phone)
    db.commit()
    db.refresh(db_phone)
    return db_phone


def update_phone(db: Session, phone_id: int, phone: schemas.CellPhoneDirectoryUpdate) -> Optional[models.CellPhoneDirectory]:
    """Update a phone"""
    db_phone = get_phone(db, phone_id)
    if db_phone:
        update_data = phone.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_phone, field, value)
        db.commit()
        db.refresh(db_phone)
    return db_phone


def delete_phone(db: Session, phone_id: int) -> bool:
    """Delete a phone (this will also delete all its associations due to cascade)"""
    db_phone = get_phone(db, phone_id)
    if db_phone:
        db.delete(db_phone)
        db.commit()
        return True
    return False


# Phone with associations
def get_phone_with_associations(db: Session, phone_id: int) -> Optional[models.CellPhoneDirectory]:
    """Get a phone with its associations"""
    return db.query(models.CellPhoneDirectory).options(
        joinedload(models.CellPhoneDirectory.associations)
    ).filter(models.CellPhoneDirectory.phone_id == phone_id).first()


def search_phones_with_associations(
    db: Session,
    search_term: Optional[str] = None,
    company_id: Optional[int] = None,
    person_id: Optional[int] = None,
    department: Optional[str] = None
) -> List[models.CellPhoneDirectory]:
    """Advanced search for phones with association filters"""
    query = db.query(models.CellPhoneDirectory).options(
        joinedload(models.CellPhoneDirectory.associations)
    )
    
    # Apply phone search filter
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            or_(
                models.CellPhoneDirectory.phone_number.like(search_pattern),
                models.CellPhoneDirectory.description.like(search_pattern)
            )
        )
    
    # Apply association filters by joining with associations table
    if company_id or person_id or department:
        query = query.join(models.CellPhoneAssociation)
        
        if company_id:
            query = query.filter(models.CellPhoneAssociation.company_id == company_id)
        
        if person_id:
            query = query.filter(models.CellPhoneAssociation.person_id == person_id)
        
        if department:
            # Search in JSON array using MySQL JSON_CONTAINS
            query = query.filter(models.CellPhoneAssociation.departments.contains([department]))
    
    return query.distinct().all()


# Association CRUD
def get_association(db: Session, association_id: int) -> Optional[models.CellPhoneAssociation]:
    """Get an association by ID"""
    return db.query(models.CellPhoneAssociation).filter(models.CellPhoneAssociation.association_id == association_id).first()


def get_associations_by_phone(db: Session, phone_id: int) -> List[models.CellPhoneAssociation]:
    """Get all associations for a specific phone"""
    return db.query(models.CellPhoneAssociation).filter(models.CellPhoneAssociation.phone_id == phone_id).all()


def create_association(db: Session, association: schemas.CellPhoneAssociationCreate) -> models.CellPhoneAssociation:
    """Create a new association"""
    db_association = models.CellPhoneAssociation(**association.model_dump())
    db.add(db_association)
    db.commit()
    db.refresh(db_association)
    return db_association


def update_association(db: Session, association_id: int, association: schemas.CellPhoneAssociationUpdate) -> Optional[models.CellPhoneAssociation]:
    """Update an association"""
    db_association = get_association(db, association_id)
    if db_association:
        update_data = association.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_association, field, value)
        db.commit()
        db.refresh(db_association)
    return db_association


def delete_association(db: Session, association_id: int) -> bool:
    """Delete an association"""
    db_association = get_association(db, association_id)
    if db_association:
        db.delete(db_association)
        db.commit()
        return True
    return False


# Combined operations
def create_phone_with_associations(
    db: Session,
    phone_data: schemas.CellPhoneDirectoryCreate,
    associations_data: List[schemas.CellPhoneAssociationCreate]
) -> Tuple[models.CellPhoneDirectory, List[models.CellPhoneAssociation]]:
    """Create a phone with associations in a single transaction"""
    
    # Consolidate associations to merge departments for same company+person combinations
    consolidated_associations = consolidate_associations(associations_data)
    
    # Create the phone first
    db_phone = create_phone(db, phone_data)
    
    # Create associations
    db_associations = []
    for assoc_data in consolidated_associations:
        assoc_data.phone_id = db_phone.phone_id
        db_association = create_association(db, assoc_data)
        db_associations.append(db_association)
    
    return db_phone, db_associations