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
    
    # Only check fields that are present in the new_obj (the update data)
    # This prevents comparing fields that weren't intended to be updated
    for key in new_obj.keys():
        old_value = old_obj.get(key)
        new_value = new_obj.get(key)
        
        # Convert values to strings for comparison
        old_str = convert_value_to_string(old_value)
        new_str = convert_value_to_string(new_value)
        
        if old_str != new_str:
            # Only log the change if it's a meaningful change
            old_is_meaningful = should_log_field_value(key, old_value, 'UPDATE')
            new_is_meaningful = should_log_field_value(key, new_value, 'UPDATE')
            
            # Log if:
            # 1. Both old and new values are meaningful (normal update)
            # 2. Old was meaningful and new is not (deletion/clearing)
            # 3. Old was not meaningful but new is meaningful (first time setting)
            if old_is_meaningful or new_is_meaningful:
                # But skip if we're going from "not meaningful" to "meaningful" 
                # AND the old value was null/None/empty (first time setting should be CREATE, not UPDATE)
                if not old_is_meaningful and new_is_meaningful:
                    if old_value is None or old_value == '' or old_value == 'None':
                        continue  # Skip logging this as an update
                
                # Skip meaningless enum value changes (like Local -> LOCAL)
                if key == 'global_operations':
                    if (old_str and new_str and 
                        old_str.lower().replace(' ', '') == new_str.lower().replace(' ', '')):
                        continue  # Same value, different case/format
                
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
            
        # Handle cases where value might be just the enum name without prefix
        if value_str in ['LOCAL', 'NATIONAL', 'MULTI_NATIONAL']:
            return value_str.replace('LOCAL', 'Local').replace('NATIONAL', 'National').replace('MULTI_NATIONAL', 'Multi National')
        
        return value_str

def should_log_field_value(field_name: str, value: Any, action_type: str = 'CREATE') -> bool:
    """Determine if a field value should be logged"""
    if value is None or value == "":
        return False
    
    # Convert value to string for easier checking
    value_str = str(value)
    
    # Skip business_operations field if it's empty/None
    if field_name == 'business_operations':
        if not value or value == 'None' or value == '' or value == 'null':
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
    
    # Skip rating fields that are None, 0, or empty (not rated), but allow 1-5
    rating_fields = ['company_brand_image', 'company_business_volume', 'company_financials', 'iisol_relationship']
    if field_name in rating_fields:
        # Only log if it's a valid rating (1-5), skip 0, null, None, empty
        try:
            rating_value = int(value) if value not in [None, '', 'None', 'null'] else 0
            if rating_value < 1 or rating_value > 5:
                return False
        except (ValueError, TypeError):
            return False
    
    # For CREATE operations, be more selective about what we skip
    if action_type == 'CREATE':
        # Only skip "None" values for optional fields when they're truly default/unset
        # But allow meaningful selections to be logged
        if field_name in ['ownership_type', 'global_operations'] and value_str == 'None':
            return False
    
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
        if should_log_field_value(field_name, value, 'CREATE'):
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
        if should_log_field_value(field_name, value, 'DELETE'):
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
    """Convert SQLAlchemy model instance to dictionary using Python attribute names"""
    if model_instance is None:
        return {}
    
    result = {}
    # Get all mapped attributes from the SQLAlchemy model
    mapper = model_instance.__class__.__mapper__
    for column_property in mapper.attrs:
        attr_name = column_property.key
        try:
            value = getattr(model_instance, attr_name)
            result[attr_name] = value
        except AttributeError:
            # If the attribute doesn't exist, skip it
            print(f"Warning: Could not access attribute {attr_name} on {model_instance.__class__.__name__}")
            continue
    return result