# persons/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from . import crud, schemas
from audit_logs.utils import create_audit_logs_for_create, create_audit_logs_for_update, create_audit_logs_for_delete, model_to_dict

router = APIRouter()

@router.post("/", response_model=schemas.Person)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    """Create a new person"""
    try:
        print(f"BACKEND: Received person data: {person.model_dump()}")
        
        # Check if NIC already exists (if provided)
        if person.nic:
            existing_person = db.query(crud.models.Person).filter(crud.models.Person.nic == person.nic).first()
            if existing_person:
                raise HTTPException(status_code=400, detail=f"Person with NIC {person.nic} already exists")
        
        result = crud.create_person(db=db, person=person)
        print(f"BACKEND: Created person with ID: {result.record_id}")
        
        # Create audit logs
        person_dict = person.model_dump(exclude_unset=True)
        audit_logs = create_audit_logs_for_create(
            db=db,
            table_name="persons",
            record_id=str(result.record_id),
            new_data=person_dict,
            user_id="system",
            user_name="System User"
        )
        print(f"AUDIT: Created {len(audit_logs)} audit log entries for person creation")
        
        # Temporarily fix age_bracket response issue
        if hasattr(result, 'age_bracket') and result.age_bracket == "":
            result.age_bracket = None
        return result
    except Exception as e:
        print(f"BACKEND: Error creating person: {e}")
        raise HTTPException(status_code=400, detail=f"Error creating person: {str(e)}")

@router.get("/", response_model=List[schemas.Person])
def read_persons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get persons with pagination"""
    try:
        persons = crud.get_persons(db, skip=skip, limit=limit)
        # Fix age_bracket validation issues
        for person in persons:
            if hasattr(person, 'age_bracket') and person.age_bracket == "":
                person.age_bracket = None
        return persons
    except Exception as e:
        print(f"BACKEND: Error getting persons: {e}")
        # If enum validation fails, try to get data without age_bracket filter
        try:
            from sqlalchemy import text
            result = db.execute(text("""
                SELECT person_id, person_print_name, full_name, gender, living_status,
                       professional_status, religion, community, base_city, attached_companies,
                       department, designation, date_of_birth, 
                       CASE 
                         WHEN age_bracket IN ('20-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90') 
                         THEN age_bracket 
                         ELSE NULL 
                       END as age_bracket, 
                       nic, record_id, created_at, updated_at
                FROM persons 
                ORDER BY person_id 
                LIMIT :limit OFFSET :skip
            """), {"limit": limit, "skip": skip})
            
            persons = []
            for row in result:
                person_dict = dict(row._mapping)
                persons.append(schemas.Person(**person_dict))
            return persons
        except Exception as e2:
            print(f"BACKEND: Fallback query also failed: {e2}")
            raise HTTPException(status_code=500, detail="Error retrieving persons")

@router.get("/all", response_model=List[schemas.Person])
def read_all_persons(db: Session = Depends(get_db)):
    """Get all persons"""
    persons = crud.get_all_persons(db)
    # Fix age_bracket validation issues
    for person in persons:
        if hasattr(person, 'age_bracket') and person.age_bracket == "":
            person.age_bracket = None
    return persons

@router.get("/search", response_model=List[schemas.Person])
def search_persons(q: str = Query(..., description="Search term"), db: Session = Depends(get_db)):
    """Search persons by name or NIC"""
    if len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Search term must be at least 2 characters")
    
    persons = crud.search_persons(db, q)
    return persons

@router.get("/by-city/{city}", response_model=List[schemas.Person])
def get_persons_by_city(city: str, db: Session = Depends(get_db)):
    """Get persons by city"""
    persons = crud.get_persons_by_city(db, city)
    return persons

@router.get("/by-community/{community}", response_model=List[schemas.Person])
def get_persons_by_community(community: str, db: Session = Depends(get_db)):
    """Get persons by community"""
    persons = crud.get_persons_by_community(db, community)
    return persons

@router.get("/cities")
def get_available_cities():
    """Get list of Pakistani cities"""
    return {"cities": schemas.PAKISTANI_CITIES}

@router.get("/{person_id}", response_model=schemas.Person)
def read_person(person_id: int, db: Session = Depends(get_db)):
    """Get a specific person by ID"""
    try:
        db_person = crud.get_person(db, record_id=person_id)
        if db_person is None:
            raise HTTPException(status_code=404, detail="Person not found")
        
        # Fix age_bracket validation issues
        if hasattr(db_person, 'age_bracket') and db_person.age_bracket == "":
            db_person.age_bracket = None
            
        return db_person
    except HTTPException:
        raise
    except Exception as e:
        print(f"BACKEND: Error getting person {person_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving person: {str(e)}")

@router.put("/{person_id}", response_model=schemas.Person)
def update_person(person_id: int, person: schemas.PersonUpdate, db: Session = Depends(get_db)):
    """Update a person"""
    try:
        # Get the existing person data for audit comparison
        existing_person = crud.get_person(db, person_id)
        if existing_person is None:
            raise HTTPException(status_code=404, detail="Person not found")
        
        # Check if NIC is being changed and if it already exists
        update_data = person.model_dump(exclude_unset=True)
        if "nic" in update_data and update_data["nic"]:
            existing_with_nic = db.query(crud.models.Person).filter(
                crud.models.Person.nic == update_data["nic"],
                crud.models.Person.record_id != person_id
            ).first()
            if existing_with_nic:
                raise HTTPException(status_code=400, detail=f"Another person with NIC {update_data['nic']} already exists")
        
        old_data = model_to_dict(existing_person)
        
        # Update the person
        db_person = crud.update_person(db, person_id, person)
        if db_person is None:
            raise HTTPException(status_code=404, detail="Person not found")
        
        # Create audit logs for changed fields
        new_data = person.model_dump(exclude_unset=True)
        audit_logs = create_audit_logs_for_update(
            db=db,
            table_name="persons",
            record_id=str(person_id),
            old_data=old_data,
            new_data=new_data,
            user_id="system",
            user_name="System User"
        )
        print(f"AUDIT: Created {len(audit_logs)} audit log entries for person update")
        
        # Temporarily fix age_bracket response issue
        if hasattr(db_person, 'age_bracket') and db_person.age_bracket == "":
            db_person.age_bracket = None
        return db_person
    except Exception as e:
        print(f"Error updating person: {e}")
        raise HTTPException(status_code=400, detail=f"Error updating person: {str(e)}")

@router.delete("/{person_id}")
def delete_person(person_id: int, db: Session = Depends(get_db)):
    """Delete a person"""
    # Get the person data before deletion for audit logging
    existing_person = crud.get_person(db, person_id)
    if existing_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    
    person_data = model_to_dict(existing_person)
    
    success = crud.delete_person(db, person_id)
    if not success:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Create audit logs for the deletion
    audit_logs = create_audit_logs_for_delete(
        db=db,
        table_name="persons",
        record_id=str(person_id),
        deleted_data=person_data,
        user_id="system",
        user_name="System User"
    )
    print(f"AUDIT: Created {len(audit_logs)} audit log entries for person deletion")
    
    return {"message": "Person deleted successfully"}