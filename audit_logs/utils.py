from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from . import schemas, crud
import json

def compare_objects(old_obj: Dict[str, Any], new_obj: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Compare two objects and return the differences
    Returns: Dict[field_name, {'old': old_value, 'new': new_value}]
    """
    changes = {}
    
    # Get all unique keys from both objects
    all_keys = set(old_obj.keys()) | set(new_obj.keys())
    
    for key in all_keys:
        old_value = old_obj.get(key)
        new_value = new_obj.get(key)
        
        # Convert values to strings for comparison
        old_str = convert_value_to_string(old_value)
        new_str = convert_value_to_string(new_value)
        
        if old_str != new_str:
            changes[key] = {
                'old': old_str,
                'new': new_str
            }
    
    return changes

def convert_value_to_string(value: Any) -> Optional[str]:
    """Convert any value to string for audit logging"""
    if value is None:
        return None
    elif isinstance(value, (list, dict)):
        return json.dumps(value, default=str, sort_keys=True)
    elif isinstance(value, bool):
        return str(value).lower()
    else:
        return str(value)

def create_audit_logs_for_create(
    db: Session,
    table_name: str,
    record_id: str,
    new_data: Dict[str, Any],
    user_id: Optional[str] = None,
    user_name: Optional[str] = None
) -> List[schemas.AuditLogResponse]:
    """Create audit logs for a CREATE operation"""
    audit_logs = []
    
    for field_name, value in new_data.items():
        # Skip None values for create operations (no point logging empty fields)
        if value is not None and value != "":
            audit_log = schemas.AuditLogCreate(
                table_name=table_name,
                record_id=str(record_id),
                field_name=field_name,
                action_type='CREATE',
                old_value=None,
                new_value=convert_value_to_string(value),
                user_id=user_id,
                user_name=user_name
            )
            audit_logs.append(audit_log)
    
    # Create logs in batch
    if audit_logs:
        db_logs = crud.create_audit_logs_batch(db, audit_logs)
        return [schemas.AuditLogResponse.from_orm(log) for log in db_logs]
    return []

def create_audit_logs_for_update(
    db: Session,
    table_name: str,
    record_id: str,
    old_data: Dict[str, Any],
    new_data: Dict[str, Any],
    user_id: Optional[str] = None,
    user_name: Optional[str] = None
) -> List[schemas.AuditLogResponse]:
    """Create audit logs for an UPDATE operation"""
    changes = compare_objects(old_data, new_data)
    audit_logs = []
    
    for field_name, change in changes.items():
        audit_log = schemas.AuditLogCreate(
            table_name=table_name,
            record_id=str(record_id),
            field_name=field_name,
            action_type='UPDATE',
            old_value=change['old'],
            new_value=change['new'],
            user_id=user_id,
            user_name=user_name
        )
        audit_logs.append(audit_log)
    
    # Create logs in batch
    if audit_logs:
        db_logs = crud.create_audit_logs_batch(db, audit_logs)
        return [schemas.AuditLogResponse.from_orm(log) for log in db_logs]
    return []

def create_audit_logs_for_delete(
    db: Session,
    table_name: str,
    record_id: str,
    deleted_data: Dict[str, Any],
    user_id: Optional[str] = None,
    user_name: Optional[str] = None
) -> List[schemas.AuditLogResponse]:
    """Create audit logs for a DELETE operation"""
    audit_logs = []
    
    for field_name, value in deleted_data.items():
        # Log all fields that had values
        if value is not None and value != "":
            audit_log = schemas.AuditLogCreate(
                table_name=table_name,
                record_id=str(record_id),
                field_name=field_name,
                action_type='DELETE',
                old_value=convert_value_to_string(value),
                new_value=None,
                user_id=user_id,
                user_name=user_name
            )
            audit_logs.append(audit_log)
    
    # Create logs in batch
    if audit_logs:
        db_logs = crud.create_audit_logs_batch(db, audit_logs)
        return [schemas.AuditLogResponse.from_orm(log) for log in db_logs]
    return []

def model_to_dict(model_instance) -> Dict[str, Any]:
    """Convert SQLAlchemy model instance to dictionary"""
    if model_instance is None:
        return {}
    
    result = {}
    for column in model_instance.__table__.columns:
        value = getattr(model_instance, column.name)
        result[column.name] = value
    return result