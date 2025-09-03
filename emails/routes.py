# emails/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from . import crud, schemas
from audit_logs.utils import create_audit_logs_for_create, create_audit_logs_for_update, create_audit_logs_for_delete, model_to_dict

router = APIRouter()

# Email Directory Routes
@router.post("/", response_model=schemas.EmailCreateResponse)
def create_email_with_associations(request: schemas.EmailCreateRequest, db: Session = Depends(get_db)):
    """Create a new email with optional associations"""
    try:
        print(f"BACKEND: Received email data: {request.email.model_dump()}")
        print(f"BACKEND: Received associations: {len(request.associations)} associations")
        
        # Check if email already exists
        existing_email = crud.get_email_by_address(db, request.email.email_address)
        if existing_email:
            raise HTTPException(status_code=400, detail=f"Email {request.email.email_address} already exists")
        
        # Create email and associations
        if request.associations:
            db_email, db_associations = crud.create_email_with_associations(
                db=db, 
                email_data=request.email, 
                associations_data=request.associations
            )
        else:
            # Create just the email
            db_email = crud.create_email(db=db, email=request.email)
            db_associations = []
        
        print(f"BACKEND: Created email with ID: {db_email.email_id}")
        
        # Create audit logs for email
        email_dict = request.email.model_dump(exclude_unset=True)
        audit_logs = create_audit_logs_for_create(
            db=db,
            table_name="email_directory",
            record_id=str(db_email.email_id),
            new_data=email_dict,
            user_id="system",
            user_name="System User"
        )
        print(f"AUDIT: Created {len(audit_logs)} audit log entries for email creation")
        
        # Create audit logs for associations
        for db_association in db_associations:
            association_dict = model_to_dict(db_association)
            association_audit_logs = create_audit_logs_for_create(
                db=db,
                table_name="email_associations",
                record_id=str(db_association.association_id),
                new_data=association_dict,
                user_id="system",
                user_name="System User"
            )
            print(f"AUDIT: Created {len(association_audit_logs)} audit log entries for association {db_association.association_id}")
        
        return schemas.EmailCreateResponse(
            email=db_email,
            associations=db_associations,
            message=f"Email created successfully with {len(db_associations)} associations"
        )
        
    except Exception as e:
        print(f"BACKEND: Error creating email: {e}")
        raise HTTPException(status_code=400, detail=f"Error creating email: {str(e)}")

@router.get("/", response_model=List[schemas.EmailDirectory])
def read_emails(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get emails with pagination"""
    emails = crud.get_emails(db, skip=skip, limit=limit)
    return emails

@router.get("/all", response_model=List[schemas.EmailDirectory])
def read_all_emails(db: Session = Depends(get_db)):
    """Get all emails"""
    emails = crud.get_all_emails(db)
    return emails

@router.get("/search", response_model=List[schemas.EmailDirectory])
def search_emails(q: str = Query(..., description="Search term"), db: Session = Depends(get_db)):
    """Search emails by address or description"""
    if len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Search term must be at least 2 characters")
    
    emails = crud.search_emails(db, q)
    return emails

@router.get("/advanced-search", response_model=List[schemas.EmailWithAssociations])
def advanced_search_emails(
    q: Optional[str] = Query(None, description="Search term"),
    company_id: Optional[int] = Query(None, description="Company ID"),
    person_id: Optional[int] = Query(None, description="Person ID"),
    department: Optional[str] = Query(None, description="Department"),
    db: Session = Depends(get_db)
):
    """Advanced search for emails with association filters"""
    emails = crud.search_emails_with_associations(
        db=db, 
        search_term=q, 
        company_id=company_id, 
        person_id=person_id, 
        department=department
    )
    return emails

@router.get("/{email_id}", response_model=schemas.EmailWithAssociations)
def read_email(email_id: int, db: Session = Depends(get_db)):
    """Get a specific email with its associations"""
    db_email = crud.get_email_with_associations(db, email_id=email_id)
    if db_email is None:
        raise HTTPException(status_code=404, detail="Email not found")
    return db_email

@router.put("/{email_id}", response_model=schemas.EmailDirectory)
def update_email(email_id: int, email: schemas.EmailDirectoryUpdate, db: Session = Depends(get_db)):
    """Update an email"""
    try:
        # Get existing email for audit comparison
        existing_email = crud.get_email(db, email_id)
        if existing_email is None:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Check if email address is being changed and if it already exists
        update_data = email.model_dump(exclude_unset=True)
        if "email_address" in update_data and update_data["email_address"]:
            existing_with_address = crud.get_email_by_address(db, update_data["email_address"])
            if existing_with_address and existing_with_address.email_id != email_id:
                raise HTTPException(status_code=400, detail=f"Email address {update_data['email_address']} already exists")
        
        old_data = model_to_dict(existing_email)
        
        # Update the email
        db_email = crud.update_email(db, email_id, email)
        if db_email is None:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Create audit logs for changed fields
        new_data = email.model_dump(exclude_unset=True)
        audit_logs = create_audit_logs_for_update(
            db=db,
            table_name="email_directory",
            record_id=str(email_id),
            old_data=old_data,
            new_data=new_data,
            user_id="system",
            user_name="System User"
        )
        print(f"AUDIT: Created {len(audit_logs)} audit log entries for email update")
        
        return db_email
    except Exception as e:
        print(f"Error updating email: {e}")
        raise HTTPException(status_code=400, detail=f"Error updating email: {str(e)}")

@router.delete("/{email_id}")
def delete_email(email_id: int, db: Session = Depends(get_db)):
    """Delete an email (this will also delete all its associations)"""
    # Get the email data before deletion for audit logging
    existing_email = crud.get_email_with_associations(db, email_id)
    if existing_email is None:
        raise HTTPException(status_code=404, detail="Email not found")
    
    email_data = model_to_dict(existing_email)
    associations_data = [model_to_dict(assoc) for assoc in existing_email.associations]
    
    success = crud.delete_email(db, email_id)
    if not success:
        raise HTTPException(status_code=404, detail="Email not found")
    
    # Create audit logs for the deletion
    audit_logs = create_audit_logs_for_delete(
        db=db,
        table_name="email_directory",
        record_id=str(email_id),
        deleted_data=email_data,
        user_id="system",
        user_name="System User"
    )
    
    # Create audit logs for deleted associations
    for assoc_data in associations_data:
        assoc_audit_logs = create_audit_logs_for_delete(
            db=db,
            table_name="email_associations",
            record_id=str(assoc_data.get('association_id')),
            deleted_data=assoc_data,
            user_id="system",
            user_name="System User"
        )
    
    print(f"AUDIT: Created {len(audit_logs)} audit log entries for email deletion")
    print(f"AUDIT: Created audit log entries for {len(associations_data)} association deletions")
    
    return {"message": "Email and all its associations deleted successfully"}

# Email Association Routes
@router.post("/{email_id}/associations", response_model=schemas.EmailAssociation)
def create_email_association(
    email_id: int, 
    association: schemas.EmailAssociationCreate, 
    db: Session = Depends(get_db)
):
    """Create a new association for an existing email"""
    try:
        # Check if email exists
        email = crud.get_email(db, email_id)
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Set the email_id
        association.email_id = email_id
        
        db_association = crud.create_association(db=db, association=association)
        
        # Create audit logs
        association_dict = association.model_dump(exclude_unset=True)
        audit_logs = create_audit_logs_for_create(
            db=db,
            table_name="email_associations",
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

@router.get("/{email_id}/associations", response_model=List[schemas.EmailAssociation])
def get_email_associations(email_id: int, db: Session = Depends(get_db)):
    """Get all associations for a specific email"""
    # Check if email exists
    email = crud.get_email(db, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    associations = crud.get_associations_by_email(db, email_id)
    return associations

@router.put("/associations/{association_id}", response_model=schemas.EmailAssociation)
def update_email_association(
    association_id: int, 
    association: schemas.EmailAssociationUpdate, 
    db: Session = Depends(get_db)
):
    """Update an email association"""
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
            table_name="email_associations",
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
def delete_email_association(association_id: int, db: Session = Depends(get_db)):
    """Delete an email association"""
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
        table_name="email_associations",
        record_id=str(association_id),
        deleted_data=association_data,
        user_id="system",
        user_name="System User"
    )
    print(f"AUDIT: Created {len(audit_logs)} audit log entries for association deletion")
    
    return {"message": "Association deleted successfully"}

# Utility routes for frontend dropdowns
@router.get("/companies/search")
def search_companies_for_email(q: str = Query(..., description="Search term"), db: Session = Depends(get_db)):
    """Search companies for email association (calls companies API internally)"""
    # This would typically call the companies service or reuse existing company search
    # For now, return a placeholder response that the frontend can use
    return {"message": "Use /companies/search endpoint"}

@router.get("/persons/search")
def search_persons_for_email(q: str = Query(..., description="Search term"), db: Session = Depends(get_db)):
    """Search persons for email association (calls persons API internally)"""
    # This would typically call the persons service or reuse existing person search
    # For now, return a placeholder response that the frontend can use
    return {"message": "Use /persons/search endpoint"}

@router.get("/departments")
def get_available_departments():
    """Get list of available departments"""
    return {"departments": [dept.value for dept in schemas.Department]}