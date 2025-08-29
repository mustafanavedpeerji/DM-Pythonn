#!/usr/bin/env python3
"""
Simple test for audit logging functionality
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from database import SessionLocal
from companies import crud, schemas
from audit_logs import crud as audit_crud

def print_audit_logs(db: Session, company_id: int):
    """Print audit logs for a company"""
    logs = audit_crud.get_audit_logs_for_record(db, "companies", str(company_id))
    if logs:
        print(f"Audit Logs for Company #{company_id}:")
        for log in logs:
            if log.action_type == "CREATE":
                print(f"  + {log.field_name}: '{log.new_value}' created")
            elif log.action_type == "UPDATE":
                print(f"  * {log.field_name}: '{log.old_value}' -> '{log.new_value}'")
            elif log.action_type == "DELETE":
                print(f"  - {log.field_name}: '{log.old_value}' deleted")
    else:
        print(f"No audit logs found for Company #{company_id}")

def test_create_company():
    """Test company creation with business operations and ratings"""
    print("\n" + "="*50)
    print("TEST: CREATE Company with Business Operations & Ratings")
    print("="*50)
    
    db = SessionLocal()
    try:
        # Create company with business operations and ratings filled
        test_company = schemas.CompanyCreate(
            company_group_print_name="Test IISOL Company",
            legal_name="IISOL Solutions Private Limited", 
            other_names="IISOL Tech, IISOL Systems",
            living_status=schemas.LivingStatus.ACTIVE,
            operations={
                "imports": True,
                "exports": True,
                "services": True,
                "manufacture": False,
                "distribution": False,
                "wholesale": False,
                "retail": False,
                "online": False,
                "soft_products": False
            },
            selected_industries=[1, 2, 3],
            founding_year="2018",
            company_size=75,
            # Status & Details fields
            established_day="15",
            established_month="March",
            # Company Assessment & Ratings
            company_brand_image=4,
            company_business_volume=5,
            company_financials=3,
            iisol_relationship=4
        )
        
        print("Creating company with business operations and ratings...")
        result = crud.create_company(db, test_company)
        print(f"Created Company ID: {result.record_id}")
        
        # Check what was stored for business operations
        print(f"Stored business_operations: '{result.business_operations}'")
        
        # Check audit logs
        print_audit_logs(db, result.record_id)
        
        return result.record_id
        
    except Exception as e:
        print(f"Error in CREATE test: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

def test_update_company(company_id: int):
    """Test updating company operations"""
    print("\n" + "="*50) 
    print("TEST: UPDATE Company Operations")
    print("="*50)
    
    db = SessionLocal()
    try:
        # Get current company
        existing = crud.get_company(db, company_id)
        if not existing:
            print(f"Company {company_id} not found")
            return
            
        print(f"Current operations: {getattr(existing, 'operations', 'None')}")
        
        # Update operations - uncheck some, check new ones
        update_data = schemas.CompanyUpdate(
            operations={
                "imports": False,    # Was True, now False
                "exports": True,     # Unchanged
                "services": False,   # Was True, now False
                "manufacture": True, # Was False, now True
                "distribution": False,
                "wholesale": False,
                "retail": True,      # Was False, now True
                "online": False,
                "soft_products": False
            }
        )
        
        print("Updating company operations...")
        result = crud.update_company(db, company_id, update_data)
        print(f"Updated Company ID: {result.record_id}")
        print(f"New business_operations: '{result.business_operations}'")
        
        print_audit_logs(db, company_id)
        
    except Exception as e:
        print(f"Error in UPDATE test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def cleanup_test_data(company_id: int):
    """Clean up test company"""
    print("\n" + "="*50)
    print("CLEANUP")
    print("="*50)
    
    db = SessionLocal()
    try:
        success = crud.delete_company(db, company_id)
        if success:
            print(f"Deleted test company {company_id}")
        else:
            print(f"Failed to delete company {company_id}")
    except Exception as e:
        print(f"Error during cleanup: {e}")
    finally:
        db.close()

def main():
    """Run audit logging tests"""
    print("AUDIT LOGGING TESTS")
    print("="*50)
    
    # Test 1: Create company with business operations and ratings
    company_id = test_create_company()
    if not company_id:
        print("CREATE test failed, aborting")
        return
    
    # Test 2: Update operations
    test_update_company(company_id)
    
    # Cleanup
    cleanup_test_data(company_id)
    
    print("\nTESTS COMPLETED")
    print("="*50)

if __name__ == "__main__":
    main()