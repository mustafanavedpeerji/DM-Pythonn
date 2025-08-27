#!/usr/bin/env python3
"""
Quick test script to check business operations functionality
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from database import SessionLocal
from companies import crud, schemas

def test_business_operations():
    print("🧪 Testing Business Operations...")
    
    db = SessionLocal()
    
    try:
        # Test data with operations
        test_company = schemas.CompanyCreate(
            company_group_print_name="Test Company",
            legal_name="Test Company Legal",
            operations={
                "imports": True,
                "exports": True,
                "services": True,
                "manufacture": False,
                "distribution": False
            }
        )
        
        print(f"📤 Creating company with operations: {test_company.operations}")
        
        # Create company
        result = crud.create_company(db, test_company)
        
        print(f"✅ Created company ID: {result.record_id}")
        print(f"💾 Stored business_operations: {result.business_operations}")
        
        # Read it back
        retrieved = crud.get_company(db, result.record_id)
        print(f"📥 Retrieved business_operations: {retrieved.business_operations}")
        
        # Clean up
        crud.delete_company(db, result.record_id)
        print("🧹 Cleaned up test company")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_business_operations()