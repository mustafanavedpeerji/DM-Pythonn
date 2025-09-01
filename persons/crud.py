# persons/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import date, datetime
from . import models, schemas

def calculate_age_bracket(birth_date: date) -> str:
    """Calculate age bracket based on birth date"""
    if not birth_date:
        return None
        
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    if age < 20:
        return None
    elif age <= 30:
        return "20-30"
    elif age <= 40:
        return "30-40"
    elif age <= 50:
        return "40-50"
    elif age <= 60:
        return "50-60"
    elif age <= 70:
        return "60-70"
    elif age <= 80:
        return "70-80"
    elif age <= 90:
        return "80-90"
    else:
        return None

def get_person(db: Session, record_id: int) -> Optional[models.Person]:
    """Get a single person by ID"""
    return db.query(models.Person).filter(models.Person.record_id == record_id).first()

def get_persons(db: Session, skip: int = 0, limit: int = 100) -> List[models.Person]:
    """Get persons with pagination"""
    return db.query(models.Person).offset(skip).limit(limit).all()

def get_all_persons(db: Session) -> List[models.Person]:
    """Get all persons"""
    return db.query(models.Person).all()

def create_person(db: Session, person: schemas.PersonCreate) -> models.Person:
    """Create a new person"""
    person_dict = person.model_dump()
    
    # Auto-calculate age bracket if date of birth is provided
    if person_dict.get("date_of_birth"):
        person_dict["age_bracket"] = calculate_age_bracket(person_dict["date_of_birth"])
    
    # Handle empty strings for optional fields
    for field in ["professional_status", "religion", "community", "base_city", "department", "designation", "nic"]:
        if person_dict.get(field) == "":
            person_dict[field] = None
    
    # Handle empty string for age_bracket specifically
    if person_dict.get("age_bracket") == "":
        person_dict["age_bracket"] = None
    
    db_person = models.Person(**person_dict)
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

def update_person(db: Session, record_id: int, person: schemas.PersonUpdate) -> Optional[models.Person]:
    """Update an existing person"""
    db_person = get_person(db, record_id)
    if db_person:
        update_data = person.model_dump(exclude_unset=True)
        
        # Auto-calculate age bracket if date of birth is being updated
        if "date_of_birth" in update_data and update_data["date_of_birth"]:
            update_data["age_bracket"] = calculate_age_bracket(update_data["date_of_birth"])
        
        # Handle empty strings for optional fields
        for field in ["professional_status", "religion", "community", "base_city", "department", "designation", "nic"]:
            if update_data.get(field) == "":
                update_data[field] = None
        
        # Handle empty string for age_bracket specifically
        if update_data.get("age_bracket") == "":
            update_data["age_bracket"] = None
                
        for field, value in update_data.items():
            setattr(db_person, field, value)
        db.commit()
        db.refresh(db_person)
    return db_person

def delete_person(db: Session, record_id: int) -> bool:
    """Delete a person"""
    db_person = get_person(db, record_id)
    if db_person:
        db.delete(db_person)
        db.commit()
        return True
    return False

def search_persons(db: Session, search_term: str) -> List[models.Person]:
    """Search persons by name or NIC"""
    search_pattern = f"%{search_term}%"
    return db.query(models.Person).filter(
        or_(
            models.Person.person_print_name.ilike(search_pattern),
            models.Person.full_name.ilike(search_pattern),
            models.Person.nic.ilike(search_pattern)
        )
    ).all()

def get_persons_by_city(db: Session, city: str) -> List[models.Person]:
    """Get persons by base city"""
    return db.query(models.Person).filter(
        or_(
            models.Person.base_city == city,
            models.Person.birth_city == city
        )
    ).all()

def get_persons_by_community(db: Session, community: str) -> List[models.Person]:
    """Get persons by community"""
    return db.query(models.Person).filter(models.Person.community == community).all()