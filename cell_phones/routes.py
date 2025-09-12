# cell_phones/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from . import crud, schemas
from audit_logs.utils import create_audit_logs_for_create, create_audit_logs_for_update, create_audit_logs_for_delete, model_to_dict

router = APIRouter()

# Cell Phone Directory Routes
@router.post("/", response_model=schemas.CellPhoneCreateResponse)
def create_phone_with_associations(request: schemas.CellPhoneCreateRequest, db: Session = Depends(get_db)):
    """Create a new phone with optional associations"""
    try:
        print(f"BACKEND: Received phone data: {request.phone.model_dump()}")
        print(f"BACKEND: Received associations: {len(request.associations)} associations")
        
        # Check if phone already exists
        existing_phone = crud.get_phone_by_number(db, request.phone.phone_number)
        if existing_phone:
            raise HTTPException(status_code=400, detail=f"Phone number {request.phone.phone_number} already exists")
        
        # Create phone and associations
        if request.associations and len(request.associations) > 0:
            # Filter out associations without company_id or person_id
            valid_associations = [
                assoc for assoc in request.associations 
                if assoc.company_id is not None or assoc.person_id is not None
            ]
            
            if valid_associations:
                db_phone, db_associations = crud.create_phone_with_associations(
                    db=db, 
                    phone_data=request.phone, 
                    associations_data=valid_associations
                )
            else:
                # Create just the phone if no valid associations
                db_phone = crud.create_phone(db=db, phone=request.phone)
                db_associations = []
        else:
            # Create just the phone
            db_phone = crud.create_phone(db=db, phone=request.phone)
            db_associations = []
        
        print(f"BACKEND: Created phone with ID: {db_phone.phone_id}")
        
        # Create audit logs for phone
        phone_dict = request.phone.model_dump(exclude_unset=True)
        audit_logs = create_audit_logs_for_create(
            db=db,
            table_name="cell_phone_directory",
            record_id=str(db_phone.phone_id),
            new_data=phone_dict,
            user_id="system",
            user_name="System User"
        )
        print(f"AUDIT: Created {len(audit_logs)} audit log entries for phone creation")
        
        # Create audit logs for associations
        for db_association in db_associations:
            association_dict = model_to_dict(db_association)
            association_audit_logs = create_audit_logs_for_create(
                db=db,
                table_name="cell_phone_associations",
                record_id=str(db_association.association_id),
                new_data=association_dict,
                user_id="system",
                user_name="System User"
            )
            print(f"AUDIT: Created {len(association_audit_logs)} audit log entries for association {db_association.association_id}")
        
        return schemas.CellPhoneCreateResponse(
            phone=db_phone,
            associations=db_associations,
            message=f"Phone created successfully with {len(db_associations)} associations"
        )
        
    except Exception as e:
        print(f"BACKEND: Error creating phone: {e}")
        raise HTTPException(status_code=400, detail=f"Error creating phone: {str(e)}")

@router.get("/", response_model=List[schemas.CellPhoneDirectory])
def read_phones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get phones with pagination"""
    phones = crud.get_phones(db, skip=skip, limit=limit)
    return phones

@router.get("/all", response_model=List[schemas.CellPhoneDirectory])
def read_all_phones(db: Session = Depends(get_db)):
    """Get all phones"""
    phones = crud.get_all_phones(db)
    return phones

@router.get("/search", response_model=List[schemas.CellPhoneDirectory])
def search_phones(q: str = Query(..., description="Search term"), db: Session = Depends(get_db)):
    """Search phones by number or description"""
    if len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Search term must be at least 2 characters")
    
    phones = crud.search_phones(db, q)
    return phones

@router.get("/advanced-search", response_model=List[schemas.CellPhoneWithAssociations])
def advanced_search_phones(
    q: Optional[str] = Query(None, description="Search term"),
    company_id: Optional[int] = Query(None, description="Company ID"),
    person_id: Optional[int] = Query(None, description="Person ID"),
    department: Optional[str] = Query(None, description="Department"),
    db: Session = Depends(get_db)
):
    """Advanced search for phones with association filters"""
    phones = crud.search_phones_with_associations(
        db=db, 
        search_term=q, 
        company_id=company_id, 
        person_id=person_id, 
        department=department
    )
    return phones

@router.get("/{phone_id}", response_model=schemas.CellPhoneWithAssociations)
def read_phone(phone_id: int, db: Session = Depends(get_db)):
    """Get a specific phone with its associations"""
    db_phone = crud.get_phone_with_associations(db, phone_id=phone_id)
    if db_phone is None:
        raise HTTPException(status_code=404, detail="Phone not found")
    return db_phone

@router.put("/{phone_id}", response_model=schemas.CellPhoneDirectory)
def update_phone(phone_id: int, phone: schemas.CellPhoneDirectoryUpdate, db: Session = Depends(get_db)):
    """Update a phone"""
    try:
        # Get existing phone for audit comparison
        existing_phone = crud.get_phone(db, phone_id)
        if existing_phone is None:
            raise HTTPException(status_code=404, detail="Phone not found")
        
        # Check if phone number is being changed and if it already exists
        update_data = phone.model_dump(exclude_unset=True)
        if "phone_number" in update_data and update_data["phone_number"]:
            existing_with_number = crud.get_phone_by_number(db, update_data["phone_number"])
            if existing_with_number and existing_with_number.phone_id != phone_id:
                raise HTTPException(status_code=400, detail=f"Phone number {update_data['phone_number']} already exists")
        
        old_data = model_to_dict(existing_phone)
        
        # Update the phone
        db_phone = crud.update_phone(db, phone_id, phone)
        if db_phone is None:
            raise HTTPException(status_code=404, detail="Phone not found")
        
        # Create audit logs for changed fields
        new_data = phone.model_dump(exclude_unset=True)
        audit_logs = create_audit_logs_for_update(
            db=db,
            table_name="cell_phone_directory",
            record_id=str(phone_id),
            old_data=old_data,
            new_data=new_data,
            user_id="system",
            user_name="System User"
        )
        print(f"AUDIT: Created {len(audit_logs)} audit log entries for phone update")
        
        return db_phone
    except Exception as e:
        print(f"Error updating phone: {e}")
        raise HTTPException(status_code=400, detail=f"Error updating phone: {str(e)}")

@router.delete("/{phone_id}")
def delete_phone(phone_id: int, db: Session = Depends(get_db)):
    """Delete a phone (this will also delete all its associations)"""
    # Get the phone data before deletion for audit logging
    existing_phone = crud.get_phone_with_associations(db, phone_id)
    if existing_phone is None:
        raise HTTPException(status_code=404, detail="Phone not found")
    
    phone_data = model_to_dict(existing_phone)
    associations_data = [model_to_dict(assoc) for assoc in existing_phone.associations]
    
    success = crud.delete_phone(db, phone_id)
    if not success:
        raise HTTPException(status_code=404, detail="Phone not found")
    
    # Create audit logs for the deletion
    audit_logs = create_audit_logs_for_delete(
        db=db,
        table_name="cell_phone_directory",
        record_id=str(phone_id),
        deleted_data=phone_data,
        user_id="system",
        user_name="System User"
    )
    
    # Create audit logs for deleted associations
    for assoc_data in associations_data:
        assoc_audit_logs = create_audit_logs_for_delete(
            db=db,
            table_name="cell_phone_associations",
            record_id=str(assoc_data.get('association_id')),
            deleted_data=assoc_data,
            user_id="system",
            user_name="System User"
        )
    
    print(f"AUDIT: Created {len(audit_logs)} audit log entries for phone deletion")
    print(f"AUDIT: Created audit log entries for {len(associations_data)} association deletions")
    
    return {"message": "Phone and all its associations deleted successfully"}

# Cell Phone Association Routes
@router.post("/{phone_id}/associations", response_model=schemas.CellPhoneAssociation)
def create_phone_association(
    phone_id: int, 
    association: schemas.CellPhoneAssociationCreate, 
    db: Session = Depends(get_db)
):
    """Create a new association for an existing phone"""
    try:
        # Check if phone exists
        phone = crud.get_phone(db, phone_id)
        if not phone:
            raise HTTPException(status_code=404, detail="Phone not found")
        
        # Set the phone_id
        association.phone_id = phone_id
        
        db_association = crud.create_association(db=db, association=association)
        
        # Create audit logs
        association_dict = association.model_dump(exclude_unset=True)
        audit_logs = create_audit_logs_for_create(
            db=db,
            table_name="cell_phone_associations",
            record_id=str(db_association.association_id),
            new_data=association_dict,
            user_id="system",
            user_name="System User"
        )
        print(f"AUDIT: Created {len(audit_logs)} audit log entries for association creation")
        
        return db_association
    except Exception as e:
        print(f"Error creating association: {e}")
        raise HTTPException(status_code=400, detail=f"Error creating association: {str(e)}")

@router.get("/{phone_id}/associations", response_model=List[schemas.CellPhoneAssociation])
def get_phone_associations(phone_id: int, db: Session = Depends(get_db)):
    """Get all associations for a specific phone"""
    # Check if phone exists
    phone = crud.get_phone(db, phone_id)
    if not phone:
        raise HTTPException(status_code=404, detail="Phone not found")
    
    associations = crud.get_associations_by_phone(db, phone_id)
    return associations

@router.put("/associations/{association_id}", response_model=schemas.CellPhoneAssociation)
def update_phone_association(
    association_id: int, 
    association: schemas.CellPhoneAssociationUpdate, 
    db: Session = Depends(get_db)
):
    """Update a phone association"""
    try:
        # Get existing association for audit comparison
        existing_association = crud.get_association(db, association_id)
        if existing_association is None:
            raise HTTPException(status_code=404, detail="Association not found")
        
        old_data = model_to_dict(existing_association)
        
        # Update the association
        db_association = crud.update_association(db, association_id, association)
        if db_association is None:
            raise HTTPException(status_code=404, detail="Association not found")
        
        # Create audit logs for changed fields
        new_data = association.model_dump(exclude_unset=True)
        audit_logs = create_audit_logs_for_update(
            db=db,
            table_name="cell_phone_associations",
            record_id=str(association_id),
            old_data=old_data,
            new_data=new_data,
            user_id="system",
            user_name="System User"
        )
        print(f"AUDIT: Created {len(audit_logs)} audit log entries for association update")
        
        return db_association
    except Exception as e:
        print(f"Error updating association: {e}")
        raise HTTPException(status_code=400, detail=f"Error updating association: {str(e)}")

@router.delete("/associations/{association_id}")
def delete_phone_association(association_id: int, db: Session = Depends(get_db)):
    """Delete a phone association"""
    # Get the association data before deletion for audit logging
    existing_association = crud.get_association(db, association_id)
    if existing_association is None:
        raise HTTPException(status_code=404, detail="Association not found")
    
    association_data = model_to_dict(existing_association)
    
    success = crud.delete_association(db, association_id)
    if not success:
        raise HTTPException(status_code=404, detail="Association not found")
    
    # Create audit logs for the deletion
    audit_logs = create_audit_logs_for_delete(
        db=db,
        table_name="cell_phone_associations",
        record_id=str(association_id),
        deleted_data=association_data,
        user_id="system",
        user_name="System User"
    )
    print(f"AUDIT: Created {len(audit_logs)} audit log entries for association deletion")
    
    return {"message": "Association deleted successfully"}

# Utility routes for frontend dropdowns
@router.get("/companies/search")
def search_companies_for_phone(q: str = Query(..., description="Search term"), db: Session = Depends(get_db)):
    """Search companies for phone association (calls companies API internally)"""
    # This would typically call the companies service or reuse existing company search
    # For now, return a placeholder response that the frontend can use
    return {"message": "Use /companies/search endpoint"}

@router.get("/persons/search")
def search_persons_for_phone(q: str = Query(..., description="Search term"), db: Session = Depends(get_db)):
    """Search persons for phone association (calls persons API internally)"""
    # This would typically call the persons service or reuse existing person search
    # For now, return a placeholder response that the frontend can use
    return {"message": "Use /persons/search endpoint"}

@router.get("/departments")
def get_available_departments():
    """Get list of available departments"""
    return {"departments": [dept.value for dept in schemas.Department]}