from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional
from . import models, schemas
from datetime import datetime

def create_audit_log(db: Session, audit_log: schemas.AuditLogCreate) -> models.AuditLog:
    """Create a single audit log entry"""
    db_audit_log = models.AuditLog(**audit_log.dict())
    db.add(db_audit_log)
    db.commit()
    db.refresh(db_audit_log)
    return db_audit_log

def create_audit_logs_batch(db: Session, audit_logs: List[schemas.AuditLogCreate]) -> List[models.AuditLog]:
    """Create multiple audit log entries in a batch"""
    db_audit_logs = []
    for audit_log in audit_logs:
        db_audit_log = models.AuditLog(**audit_log.dict())
        db.add(db_audit_log)
        db_audit_logs.append(db_audit_log)
    
    db.commit()
    for db_audit_log in db_audit_logs:
        db.refresh(db_audit_log)
    return db_audit_logs

def get_audit_logs(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    table_name: Optional[str] = None,
    record_id: Optional[str] = None,
    action_type: Optional[str] = None,
    field_name: Optional[str] = None,
    user_id: Optional[str] = None
) -> List[models.AuditLog]:
    """Get audit logs with optional filtering"""
    query = db.query(models.AuditLog)
    
    # Apply filters
    if table_name:
        query = query.filter(models.AuditLog.table_name == table_name)
    if record_id:
        query = query.filter(models.AuditLog.record_id == record_id)
    if action_type:
        query = query.filter(models.AuditLog.action_type == action_type)
    if field_name:
        query = query.filter(models.AuditLog.field_name == field_name)
    if user_id:
        query = query.filter(models.AuditLog.user_id == user_id)
    
    return query.order_by(desc(models.AuditLog.timestamp)).offset(skip).limit(limit).all()

def get_audit_logs_for_record(db: Session, table_name: str, record_id: str) -> List[models.AuditLog]:
    """Get all audit logs for a specific record"""
    return db.query(models.AuditLog).filter(
        and_(models.AuditLog.table_name == table_name, models.AuditLog.record_id == record_id)
    ).order_by(desc(models.AuditLog.timestamp)).all()

def get_recent_audit_logs(db: Session, limit: int = 50) -> List[models.AuditLog]:
    """Get the most recent audit logs"""
    return db.query(models.AuditLog).order_by(desc(models.AuditLog.timestamp)).limit(limit).all()