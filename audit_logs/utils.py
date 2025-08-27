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
            # Only log the change if at least one of the values is meaningful
            # This prevents logging changes from empty to empty or false to false
            if should_log_field_value(key, old_value) or should_log_field_value(key, new_value):
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
        value_str = str(value)
        
        # Clean up enum values to be more readable
        # CompanyType.COMPANY -> Company
        if 'CompanyType.' in value_str:
            return value_str.replace('CompanyType.', '').replace('COMPANY', 'Company').replace('GROUP', 'Group').replace('DIVISION', 'Division')
        
        # BusinessActivity.N -> No, BusinessActivity.Y -> Yes  
        if 'BusinessActivity.' in value_str:
            return value_str.replace('BusinessActivity.N', 'No').replace('BusinessActivity.Y', 'Yes')
        
        # LivingStatus.ACTIVE -> Active
        if 'LivingStatus.' in value_str:
            return value_str.replace('LivingStatus.', '').replace('ACTIVE', 'Active').replace('INACTIVE', 'Inactive').replace('DORMANT', 'Dormant').replace('IN_PROCESS', 'In Process')
        
        # OwnershipType enums (if any)
        if 'OwnershipType.' in value_str:
            return value_str.replace('OwnershipType.', '')
        
        # GlobalOperations enums (if any)  
        if 'GlobalOperations.' in value_str:
            return value_str.replace('GlobalOperations.', '')
        
        return value_str

def should_log_field_value(field_name: str, value: Any) -> bool:
    """Determine if a field value should be logged"""
    if value is None or value == "":
        return False
    
    # Convert value to string for easier checking
    value_str = str(value)
    
    # Skip business_operations field if it's empty/None
    if field_name == 'business_operations':
        if not value or value == 'None' or value == '':
            return False
    
    # Skip legacy boolean fields (these are now handled by business_operations)
    legacy_boolean_fields = [
        'imports', 'exports', 'manufacture', 'distribution', 
        'wholesale', 'retail', 'services', 'online', 'soft_products'
    ]
    if field_name in legacy_boolean_fields:
        # Skip if value is N, False, or contains BusinessActivity.N
        if (value == False or value == 'N' or value == 'false' or 
            'BusinessActivity.N' in value_str or value_str == 'N'):
            return False
    
    # Skip empty arrays/lists (like unselected industries)
    if isinstance(value, (list, tuple)) and len(value) == 0:
        return False
    
    # Skip JSON strings that represent empty arrays or None
    if isinstance(value, str) and value.strip() in ['[]', '{}', 'null', 'None']:
        return False
    
    # Skip if string value is "None" 
    if value_str == 'None':
        return False
    
    # Skip industries field if no industries are selected
    if field_name == 'selected_industries':
        # Skip if it's empty array, None, null string, or empty JSON
        if (not value or value == 'None' or value == '[]' or 
            value == 'null' or value == '' or
            (isinstance(value, str) and value.strip() in ['[]', '{}', 'null', 'None']) or
            (isinstance(value, (list, tuple)) and len(value) == 0)):
            return False
    
    # Skip rating fields that are None or 0 (not rated)
    rating_fields = ['company_brand_image', 'company_business_volume', 'company_financials', 'iisol_relationship']
    if field_name in rating_fields and (value is None or value == 0 or value == '0'):
        return False
    
    # Don't skip default enum values - we want to log Active status when set
    # (Removed the skip logic for Active status)
        
    return True

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
        # Only log fields that have meaningful values
        if should_log_field_value(field_name, value):
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
        # Only log fields that had meaningful values
        if should_log_field_value(field_name, value):
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