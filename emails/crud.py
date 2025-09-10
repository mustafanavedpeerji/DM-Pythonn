# emails/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from . import models, schemas

# Email Directory CRUD Operations
def get_email(db: Session, email_id: int) -> Optional[models.EmailDirectory]:
    """Get a single email by ID"""
    return db.query(models.EmailDirectory).filter(models.EmailDirectory.email_id == email_id).first()

def get_email_by_address(db: Session, email_address: str) -> Optional[models.EmailDirectory]:
    """Get email by email address"""
    return db.query(models.EmailDirectory).filter(models.EmailDirectory.email_address == email_address.lower()).first()

def get_emails(db: Session, skip: int = 0, limit: int = 100) -> List[models.EmailDirectory]:
    """Get emails with pagination"""
    return db.query(models.EmailDirectory).offset(skip).limit(limit).all()

def get_all_emails(db: Session) -> List[models.EmailDirectory]:
    """Get all emails"""
    return db.query(models.EmailDirectory).all()

def create_email(db: Session, email: schemas.EmailDirectoryCreate) -> models.EmailDirectory:
    """Create a new email directory entry"""
    email_dict = email.model_dump()
    
    # Ensure email is lowercase
    email_dict["email_address"] = email_dict["email_address"].lower()
    
    db_email = models.EmailDirectory(**email_dict)
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    return db_email

def update_email(db: Session, email_id: int, email: schemas.EmailDirectoryUpdate) -> Optional[models.EmailDirectory]:
    """Update an existing email"""
    db_email = get_email(db, email_id)
    if db_email:
        update_data = email.model_dump(exclude_unset=True)
        
        # Ensure email is lowercase if being updated
        if "email_address" in update_data:
            update_data["email_address"] = update_data["email_address"].lower()
            
        for field, value in update_data.items():
            setattr(db_email, field, value)
        db.commit()
        db.refresh(db_email)
    return db_email

def delete_email(db: Session, email_id: int) -> bool:
    """Delete an email (this will also delete associated associations due to cascade)"""
    db_email = get_email(db, email_id)
    if db_email:
        db.delete(db_email)
        db.commit()
        return True
    return False

def search_emails(db: Session, search_term: str) -> List[models.EmailDirectory]:
    """Search emails by email address or description"""
    search_pattern = f"%{search_term}%"
    return db.query(models.EmailDirectory).filter(
        or_(
            models.EmailDirectory.email_address.ilike(search_pattern),
            models.EmailDirectory.description.ilike(search_pattern)
        )
    ).all()

# Email Association CRUD Operations
def get_association(db: Session, association_id: int) -> Optional[models.EmailAssociation]:
    """Get a single association by ID"""
    return db.query(models.EmailAssociation).filter(models.EmailAssociation.association_id == association_id).first()

def get_associations_by_email(db: Session, email_id: int) -> List[models.EmailAssociation]:
    """Get all associations for a specific email"""
    return db.query(models.EmailAssociation).filter(models.EmailAssociation.email_id == email_id).all()

def get_associations_by_company(db: Session, company_id: int) -> List[models.EmailAssociation]:
    """Get all email associations for a specific company"""
    return db.query(models.EmailAssociation).filter(models.EmailAssociation.company_id == company_id).all()

def get_associations_by_person(db: Session, person_id: int) -> List[models.EmailAssociation]:
    """Get all email associations for a specific person"""
    return db.query(models.EmailAssociation).filter(models.EmailAssociation.person_id == person_id).all()

def get_associations_by_department(db: Session, department: str) -> List[models.EmailAssociation]:
    """Get all email associations for a specific department"""
    # Use JSON search since departments is now a JSON array
    return db.query(models.EmailAssociation).filter(
        models.EmailAssociation.departments.contains([department])
    ).all()

def create_association(db: Session, association: schemas.EmailAssociationCreate) -> models.EmailAssociation:
    """Create a new email association"""
    association_dict = association.model_dump()
    
    db_association = models.EmailAssociation(**association_dict)
    db.add(db_association)
    db.commit()
    db.refresh(db_association)
    return db_association

def update_association(db: Session, association_id: int, association: schemas.EmailAssociationUpdate) -> Optional[models.EmailAssociation]:
    """Update an existing association"""
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

def create_associations_bulk(db: Session, associations: List[schemas.EmailAssociationCreate]) -> List[models.EmailAssociation]:
    """Create multiple associations at once"""
    db_associations = []
    for association in associations:
        association_dict = association.model_dump()
        db_association = models.EmailAssociation(**association_dict)
        db.add(db_association)
        db_associations.append(db_association)
    
    db.commit()
    for db_association in db_associations:
        db.refresh(db_association)
    
    return db_associations

# Combined Operations
def get_email_with_associations(db: Session, email_id: int) -> Optional[models.EmailDirectory]:
    """Get email with all its associations"""
    return db.query(models.EmailDirectory).filter(models.EmailDirectory.email_id == email_id).first()

def consolidate_associations(associations_data: List[schemas.EmailAssociationCreate]) -> List[schemas.EmailAssociationCreate]:
    """Consolidate associations - merge departments for same company/person"""
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

def create_email_with_associations(db: Session, email_data: schemas.EmailDirectoryCreate, 
                                  associations_data: List[schemas.EmailAssociationCreate]) -> tuple:
    """Create email and its associations in a single transaction"""
    # Create the email first
    email_dict = email_data.model_dump()
    email_dict["email_address"] = email_dict["email_address"].lower()
    
    db_email = models.EmailDirectory(**email_dict)
    db.add(db_email)
    db.flush()  # Flush to get the email_id without committing
    
    # Consolidate associations to avoid multiple rows for same company with different departments
    consolidated_associations = consolidate_associations(associations_data)
    
    # Create associations
    db_associations = []
    for association_data in consolidated_associations:
        association_dict = association_data.model_dump()
        association_dict["email_id"] = db_email.email_id
        
        db_association = models.EmailAssociation(**association_dict)
        db.add(db_association)
        db_associations.append(db_association)
    
    db.commit()
    db.refresh(db_email)
    for db_association in db_associations:
        db.refresh(db_association)
    
    return db_email, db_associations

def search_emails_with_associations(db: Session, search_term: str = None, 
                                   company_id: int = None, person_id: int = None, 
                                   department: str = None) -> List[models.EmailDirectory]:
    """Advanced search for emails with association filters"""
    query = db.query(models.EmailDirectory).join(models.EmailAssociation, isouter=True)
    
    conditions = []
    
    if search_term:
        search_pattern = f"%{search_term}%"
        conditions.append(
            or_(
                models.EmailDirectory.email_address.ilike(search_pattern),
                models.EmailDirectory.description.ilike(search_pattern)
            )
        )
    
    if company_id:
        conditions.append(models.EmailAssociation.company_id == company_id)
    
    if person_id:
        conditions.append(models.EmailAssociation.person_id == person_id)
        
    if department:
        conditions.append(models.EmailAssociation.departments.contains([department]))
    
    if conditions:
        query = query.filter(and_(*conditions))
    
    return query.distinct().all()