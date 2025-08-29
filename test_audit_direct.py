#!/usr/bin/env python3
"""
Direct test of audit logging utilities
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from database import SessionLocal
from companies import crud, schemas
from audit_logs import crud as audit_crud
from audit_logs.utils import create_audit_logs_for_create, should_log_field_value

def test_audit_utils_directly():
    """Test audit logging utilities directly"""
    print("TESTING AUDIT LOGGING UTILITIES DIRECTLY")
    print("="*50)
    
    db = SessionLocal()
    try:
        # Test should_log_field_value function
        print("\n1. Testing should_log_field_value function:")
        test_cases = [
            ("company_group_print_name", "Test Company", "CREATE"),
            ("business_operations", "imports, exports", "CREATE"), 
            ("company_brand_image", 4, "CREATE"),
            ("company_size", 75, "CREATE"),
            ("selected_industries", "[1, 2, 3]", "CREATE"),
            ("parent_id", None, "CREATE"),
            ("ownership_type", None, "CREATE"),
        ]
        
        for field_name, value, action_type in test_cases:
            should_log = should_log_field_value(field_name, value, action_type)
            print(f"  {field_name}: {value} -> {should_log}")
        
        # Test create_audit_logs_for_create function directly
        print("\n2. Testing create_audit_logs_for_create directly:")
        test_data = {
            "company_group_print_name": "Test Company Direct",
            "business_operations": "imports, exports",
            "company_brand_image": 4,
            "selected_industries": "[1, 2, 3]",
            "parent_id": None,  # Should be skipped
            "ownership_type": None,  # Should be skipped
        }
        
        audit_logs = create_audit_logs_for_create(
            db=db,
            table_name="companies", 
            record_id="999",
            new_data=test_data,
            user_id="test_user",
            user_name="Test User"
        )
        
        print(f"Created {len(audit_logs)} audit log entries:")
        for log in audit_logs:
            print(f"  - {log.field_name}: {log.new_value}")
        
        # Check if logs were actually saved
        saved_logs = audit_crud.get_audit_logs_for_record(db, "companies", "999")
        print(f"Found {len(saved_logs)} saved logs in database")
        
        # Clean up test logs
        for log in saved_logs:
            db.delete(log)
        db.commit()
        print("Cleaned up test logs")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def test_company_create_with_debug():
    """Test company creation with debug output"""
    print("\n" + "="*50)
    print("TESTING COMPANY CREATE WITH DEBUG")
    print("="*50)
    
    db = SessionLocal()
    try:
        # Create simple company
        test_company = schemas.CompanyCreate(
            company_group_print_name="Debug Test Company",
            legal_name="Debug Test Legal Name",
            operations={
                "imports": True,
                "services": True,
            }
        )
        
        print("Creating company...")
        result = crud.create_company(db, test_company)
        print(f"Created company ID: {result.record_id}")
        print(f"Business operations stored: '{result.business_operations}'")
        
        # Manually create audit logs to test
        print("\nManually creating audit logs...")
        company_dict = test_company.dict(exclude_unset=True)
        print(f"Company dict: {company_dict}")
        
        audit_logs = create_audit_logs_for_create(
            db=db,
            table_name="companies",
            record_id=str(result.record_id),
            new_data=company_dict,
            user_id="manual_test",
            user_name="Manual Test User"
        )
        
        print(f"Manually created {len(audit_logs)} audit logs")
        
        # Check saved logs
        saved_logs = audit_crud.get_audit_logs_for_record(db, "companies", str(result.record_id))
        print(f"Found {len(saved_logs)} logs in database:")
        for log in saved_logs:
            print(f"  {log.field_name}: {log.new_value}")
        
        # Cleanup
        crud.delete_company(db, result.record_id)
        print(f"Deleted test company {result.record_id}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_audit_utils_directly()
    test_company_create_with_debug()