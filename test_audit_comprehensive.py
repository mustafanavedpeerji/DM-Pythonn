#!/usr/bin/env python3
"""
Comprehensive test for audit logging functionality
Tests all three scenarios:
1. CREATE: Only logs fields that user actually filled
2. UPDATE: Only logs fields that were actually changed  
3. DELETE: Logs when fields are backspaced/cleared
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from database import SessionLocal
from companies import crud, schemas
from audit_logs import crud as audit_crud
from audit_logs.utils import create_audit_logs_for_create, create_audit_logs_for_update, model_to_dict

def print_audit_logs(db: Session, company_id: int):
    """Print audit logs for a company"""
    logs = audit_crud.get_audit_logs_for_record(db, "companies", str(company_id))
    if logs:
        print(f"📋 Audit Logs for Company #{company_id}:")
        for log in logs:
            action_icon = {"CREATE": "➕", "UPDATE": "✏️", "DELETE": "❌"}.get(log.action_type, "📝")
            if log.action_type == "CREATE":
                print(f"  {action_icon} {log.field_name}: \"{log.new_value}\" created")
            elif log.action_type == "UPDATE":
                print(f"  {action_icon} {log.field_name}: \"{log.old_value}\" → \"{log.new_value}\"")
            elif log.action_type == "DELETE":
                print(f"  {action_icon} {log.field_name}: \"{log.old_value}\" deleted")
    else:
        print(f"❌ No audit logs found for Company #{company_id}")

def test_scenario_1_create():
    """Test 1: CREATE - Only logs fields user actually filled"""
    print("\n" + "="*60)
    print("TEST 1: CREATE - Selective Field Logging")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Create company with ONLY some fields filled (like real user input)
        test_company = schemas.CompanyCreate(
            company_group_print_name="Test IISOL",  # ✅ User filled
            legal_name="IISOL Solutions Ltd",       # ✅ User filled  
            other_names="IISOL Tech",               # ✅ User filled
            living_status=schemas.LivingStatus.ACTIVE,  # ✅ User selected
            operations={                            # ✅ User checked some
                "imports": True,
                "exports": True, 
                "services": True,
                "manufacture": False,  # ❌ Not checked
                "distribution": False, # ❌ Not checked
                "wholesale": False,    # ❌ Not checked
                "retail": False,       # ❌ Not checked
                "online": False,       # ❌ Not checked
                "soft_products": False # ❌ Not checked
            },
            selected_industries=[1, 2, 3],          # ✅ User selected
            founding_year="2018",                   # ✅ User filled
            # NOT filled by user (should NOT create logs):
            # - parent_id (null)
            # - ownership_type (null) 
            # - global_operations (null)
            # - established_day (null)
            # - established_month (null)
            # - company_size (null)
            # - ntn_no (null)
            # - websites (empty)
            # - ratings (all null)
        )
        
        print(f"Creating company with selective fields...")
        result = crud.create_company(db, test_company)
        print(f"Created Company ID: {result.record_id}")
        
        # Check what was actually stored
        print(f"Stored business_operations: '{result.business_operations}'")
        
        # Check audit logs
        print_audit_logs(db, result.record_id)
        
        print("\nExpected logs:")
        print("  + company_group_print_name, legal_name, other_names")
        print("  + living_status, business_operations, selected_industries, founding_year")
        print("Should NOT log:")
        print("  - parent_id, ownership_type, global_operations (null/empty)")
        print("  - established_day, established_month, company_size (null)")
        print("  - ntn_no, websites (empty)")
        print("  - rating fields (null/0)")
        
        return result.record_id
        
    except Exception as e:
        print(f"Error in CREATE test: {e}")
        return None
    finally:
        db.close()

def test_scenario_2_update(company_id: int):
    """Test 2: UPDATE - Only logs fields that were actually changed"""
    print("\n" + "="*60)
    print("TEST 2: UPDATE - Only Changed Fields")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Get current company state
        existing = crud.get_company(db, company_id)
        if not existing:
            print(f"❌ Company {company_id} not found")
            return
            
        print(f"Current company name: '{existing.company_group_print_name}'")
        print(f"Current status: '{existing.living_status}'")
        
        # Update with ONLY 2 fields changed (like real user edit)
        update_data = schemas.CompanyUpdate(
            company_group_print_name="IISOL Solutions Updated",  # ✅ Changed
            living_status=schemas.LivingStatus.DORMANT,          # ✅ Changed
            # These fields are sent but not changed:
            legal_name="IISOL Solutions Ltd",  # ❌ Same value
            other_names="IISOL Tech",          # ❌ Same value  
            founding_year="2018"               # ❌ Same value
        )
        
        print(f"📤 Updating company with selective changes...")
        result = crud.update_company(db, company_id, update_data)
        print(f"✅ Updated Company ID: {result.record_id}")
        
        print_audit_logs(db, company_id)
        
        print("\n✅ Expected UPDATE logs (only changed fields):")
        print("  ✏️ company_group_print_name: 'Test IISOL' → 'IISOL Solutions Updated'")
        print("  ✏️ living_status: 'Active' → 'Dormant'")
        print("❌ Should NOT log (unchanged fields):")
        print("  ❌ legal_name, other_names, founding_year (same values)")
        
    except Exception as e:
        print(f"❌ Error in UPDATE test: {e}")
    finally:
        db.close()

def test_scenario_3_deletion(company_id: int):
    """Test 3: DELETE fields (backspace to empty)"""
    print("\n" + "="*60)
    print("TEST 3: DELETE - Backspaced Fields")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Get current company state
        existing = crud.get_company(db, company_id)
        print(f"📥 Current other_names: '{existing.other_names}'")
        print(f"📥 Current founding_year: '{existing.founding_year}'")
        
        # Update by clearing some fields (user backspaced them)
        update_data = schemas.CompanyUpdate(
            other_names="",          # ✅ User backspaced this field
            founding_year=None,      # ✅ User cleared this field
            operations={             # ✅ User unchecked all operations
                "imports": False,
                "exports": False, 
                "services": False
            }
        )
        
        print(f"📤 Clearing fields (simulating backspace/delete)...")
        result = crud.update_company(db, company_id, update_data)
        print(f"✅ Updated Company ID: {result.record_id}")
        
        print_audit_logs(db, company_id)
        
        print("\n✅ Expected DELETE logs (cleared fields):")
        print("  ✏️ other_names: 'IISOL Tech' → 'Empty'")
        print("  ✏️ founding_year: '2018' → 'Not Set'")
        print("  ✏️ business_operations: 'imports, exports, services' → 'Not Set'")
        
    except Exception as e:
        print(f"❌ Error in DELETE test: {e}")
    finally:
        db.close()

def test_cleanup(company_id: int):
    """Clean up test data"""
    print("\n" + "="*60)
    print("CLEANUP")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Delete company and its audit logs
        success = crud.delete_company(db, company_id)
        if success:
            print(f"✅ Deleted test company {company_id}")
        else:
            print(f"❌ Failed to delete company {company_id}")
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
    finally:
        db.close()

def main():
    """Run comprehensive audit logging tests"""
    print("COMPREHENSIVE AUDIT LOGGING TESTS")
    print("="*60)
    print("Testing all 3 scenarios:")
    print("1. CREATE: Only user-filled fields get logged")  
    print("2. UPDATE: Only changed fields get logged")
    print("3. DELETE: Cleared fields get logged as deletions")
    
    # Test 1: CREATE
    company_id = test_scenario_1_create()
    if not company_id:
        print("❌ CREATE test failed, aborting remaining tests")
        return
    
    # Test 2: UPDATE 
    test_scenario_2_update(company_id)
    
    # Test 3: DELETE (field clearing)
    test_scenario_3_deletion(company_id)
    
    # Cleanup
    test_cleanup(company_id)
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
    print("Check the output above to verify audit logging is working correctly!")

if __name__ == "__main__":
    main()