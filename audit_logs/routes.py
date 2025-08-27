from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from . import crud, schemas

router = APIRouter(prefix="/audit-logs", tags=["audit_logs"])

@router.get("/", response_model=List[schemas.AuditLogResponse])
def get_audit_logs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    table_name: Optional[str] = Query(None, description="Filter by table name"),
    record_id: Optional[str] = Query(None, description="Filter by record ID"),
    action_type: Optional[str] = Query(None, description="Filter by action type (CREATE, UPDATE, DELETE)"),
    field_name: Optional[str] = Query(None, description="Filter by field name"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db)
):
    """Get audit logs with optional filtering"""
    try:
        logs = crud.get_audit_logs(
            db=db, 
            skip=skip, 
            limit=limit,
            table_name=table_name,
            record_id=record_id,
            action_type=action_type,
            field_name=field_name,
            user_id=user_id
        )
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving audit logs: {str(e)}")

@router.get("/record/{table_name}/{record_id}", response_model=List[schemas.AuditLogResponse])
def get_audit_logs_for_record(
    table_name: str,
    record_id: str,
    db: Session = Depends(get_db)
):
    """Get all audit logs for a specific record"""
    try:
        logs = crud.get_audit_logs_for_record(db=db, table_name=table_name, record_id=record_id)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving audit logs for record: {str(e)}")

@router.get("/recent", response_model=List[schemas.AuditLogResponse])
def get_recent_audit_logs(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of recent logs to return"),
    db: Session = Depends(get_db)
):
    """Get the most recent audit logs"""
    try:
        logs = crud.get_recent_audit_logs(db=db, limit=limit)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving recent audit logs: {str(e)}")

@router.post("/", response_model=schemas.AuditLogResponse)
def create_audit_log(
    audit_log: schemas.AuditLogCreate,
    db: Session = Depends(get_db)
):
    """Create a single audit log entry"""
    try:
        return crud.create_audit_log(db=db, audit_log=audit_log)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating audit log: {str(e)}")

@router.post("/batch", response_model=List[schemas.AuditLogResponse])
def create_audit_logs_batch(
    audit_logs: schemas.AuditLogBatch,
    db: Session = Depends(get_db)
):
    """Create multiple audit log entries in a batch"""
    try:
        return crud.create_audit_logs_batch(db=db, audit_logs=audit_logs.logs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating audit logs batch: {str(e)}")