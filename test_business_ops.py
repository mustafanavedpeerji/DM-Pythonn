#!/usr/bin/env python3
"""
Test business operations saving specifically
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from database import SessionLocal
from companies import crud, schemas
from companies.models import Company

def test_business_operations_direct():
    """Test business operations saving directly"""
    print("TESTING BUSINESS OPERATIONS SAVING DIRECTLY")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Test 1: Create company with business operations
        print("1. Creating company with business operations...")
        
        test_company = schemas.CompanyCreate(
            company_group_print_name="Business Ops Test Company",
            legal_name="Business Ops Test Legal",
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
            }
        )
        
        print(f"Input operations: {test_company.operations}")
        
        # Create company via CRUD
        result = crud.create_company(db, test_company)
        print(f"Created company ID: {result.record_id}")
        print(f"Stored business_operations: '{result.business_operations}'")
        
        # Check what's actually in database
        print("\n2. Checking database directly...")
        db_record = db.query(Company).filter(Company.record_id == result.record_id).first()
        if db_record:
            print(f"Direct DB business_operations: '{db_record.business_operations}'")
            print(f"DB record type: {type(db_record.business_operations)}")
            print(f"DB record is None: {db_record.business_operations is None}")
            print(f"DB record is empty string: {db_record.business_operations == ''}")
        else:
            print("Could not find record in database!")
            
        # Test 2: Retrieve via get_company (which adds operations object)
        print("\n3. Testing retrieval via get_company...")
        retrieved = crud.get_company(db, result.record_id)
        if retrieved:
            print(f"Retrieved business_operations: '{retrieved.business_operations}'")
            print(f"Retrieved operations object: {getattr(retrieved, 'operations', 'NOT FOUND')}")
        else:
            print("Could not retrieve company!")
            
        # Test 3: Update operations
        print("\n4. Testing update operations...")
        update_data = schemas.CompanyUpdate(
            operations={
                "imports": False,
                "exports": True,
                "manufacture": True,
                "retail": True,
                "services": False,
                "distribution": False,
                "wholesale": False,
                "online": False,
                "soft_products": False
            }
        )
        
        print(f"Update operations: {update_data.operations}")
        
        updated = crud.update_company(db, result.record_id, update_data)
        if updated:
            print(f"Updated business_operations: '{updated.business_operations}'")
            
            # Check database directly again
            db_record_updated = db.query(Company).filter(Company.record_id == result.record_id).first()
            print(f"Direct DB after update: '{db_record_updated.business_operations}'")
        else:
            print("Update failed!")
        
        # Cleanup
        crud.delete_company(db, result.record_id)
        print(f"\nCleaned up company {result.record_id}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_business_operations_direct()