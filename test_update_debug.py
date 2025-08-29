#!/usr/bin/env python3
"""
Debug UPDATE audit logging specifically
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

import requests
import json
from sqlalchemy.orm import Session
from database import SessionLocal
from audit_logs import crud as audit_crud
from companies import crud as company_crud
from audit_logs.utils import model_to_dict, compare_objects

BASE_URL = "http://localhost:8000/companies"

def debug_update_audit():
    """Debug why UPDATE audit logs aren't created"""
    print("DEBUGGING UPDATE AUDIT LOGGING")
    print("="*50)
    
    # First create a company via API
    company_data = {
        "company_group_print_name": "Update Test Company",
        "legal_name": "Update Test Legal",
        "operations": {
            "imports": True,
            "exports": False,
            "services": True,
            "manufacture": False,
            "distribution": False,
            "wholesale": False,
            "retail": False,
            "online": False,
            "soft_products": False
        }
    }
    
    print("1. Creating test company...")
    response = requests.post(BASE_URL, json=company_data)
    if response.status_code != 200:
        print(f"Failed to create company: {response.text}")
        return
    
    company = response.json()
    company_id = company["record_id"]
    print(f"Created company {company_id}")
    
    # Now test the update logic directly
    db = SessionLocal()
    try:
        print("\n2. Testing model_to_dict and compare_objects...")
        
        # Get the existing company from database
        existing = company_crud.get_company(db, company_id)
        if not existing:
            print("Company not found!")
            return
        
        print(f"Found existing company: {existing.company_group_print_name}")
        
        # Convert to dict
        old_data = model_to_dict(existing)
        print(f"Old data keys: {list(old_data.keys())}")
        print(f"Old operations: {old_data.get('operations', 'Not found')}")
        print(f"Old business_operations: {old_data.get('business_operations', 'Not found')}")
        
        # Simulate update data (what the API receives)
        new_data = {
            "operations": {
                "imports": False,   # Changed from True
                "exports": True,    # Changed from False  
                "services": True,   # Unchanged
                "manufacture": True, # Changed from False
                "distribution": False,
                "wholesale": False,
                "retail": False,
                "online": False,
                "soft_products": False
            }
        }
        
        print(f"\nNew data: {new_data}")
        
        # Test compare_objects function
        changes = compare_objects(old_data, new_data)
        print(f"\nChanges detected: {len(changes)}")
        for field_name, change in changes.items():
            print(f"  {field_name}: '{change['old']}' -> '{change['new']}'")
        
        # Now test via actual API update
        print(f"\n3. Testing via API update...")
        update_response = requests.put(f"{BASE_URL}/{company_id}", json=new_data)
        if update_response.status_code == 200:
            result = update_response.json()
            print(f"Updated successfully. New business_operations: {result.get('business_operations')}")
        else:
            print(f"API update failed: {update_response.text}")
        
        # Check audit logs
        print(f"\n4. Checking audit logs...")
        logs = audit_crud.get_audit_logs_for_record(db, "companies", str(company_id))
        update_logs = [log for log in logs if log.action_type == "UPDATE"]
        print(f"Found {len(update_logs)} UPDATE audit logs:")
        for log in update_logs:
            print(f"  {log.field_name}: '{log.old_value}' -> '{log.new_value}'")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        try:
            requests.delete(f"{BASE_URL}/{company_id}")
            print(f"\nCleaned up company {company_id}")
        except:
            pass
        db.close()

if __name__ == "__main__":
    debug_update_audit()