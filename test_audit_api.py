#!/usr/bin/env python3
"""
Test audit logging via API endpoints
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

import requests
import json
from sqlalchemy.orm import Session
from database import SessionLocal
from audit_logs import crud as audit_crud

BASE_URL = "http://localhost:8000/companies"

def print_audit_logs(company_id: int):
    """Print audit logs for a company"""
    db = SessionLocal()
    try:
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
    finally:
        db.close()

def test_api_create():
    """Test company creation via API"""
    print("TESTING COMPANY CREATION VIA API")
    print("="*50)
    
    # Create company data
    company_data = {
        "company_group_print_name": "API Test Company",
        "legal_name": "API Test Legal Name",
        "other_names": "API Test Other Names",
        "living_status": "Active",
        "operations": {
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
        "selected_industries": [1, 2, 3],
        "founding_year": "2020",
        "company_size": 50,
        "established_day": "10",
        "established_month": "January",
        "company_brand_image": 4,
        "company_business_volume": 5,
        "company_financials": 3,
        "iisol_relationship": 4
    }
    
    try:
        print("Creating company via API...")
        response = requests.post(BASE_URL, json=company_data)
        
        if response.status_code == 200:
            result = response.json()
            company_id = result["record_id"]
            print(f"Created Company ID: {company_id}")
            print(f"Business operations: {result.get('business_operations', 'Not found')}")
            
            # Check audit logs
            print_audit_logs(company_id)
            
            return company_id
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server.")
        print("Make sure the FastAPI server is running on http://localhost:8000")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_api_update(company_id: int):
    """Test company update via API"""
    print(f"\nTESTING COMPANY UPDATE VIA API")
    print("="*50)
    
    # Update data - change operations
    update_data = {
        "operations": {
            "imports": False,    # Was True
            "exports": True,     # Unchanged
            "services": False,   # Was True  
            "manufacture": True, # Was False
            "distribution": False,
            "wholesale": False,
            "retail": True,      # Was False
            "online": False,
            "soft_products": False
        }
    }
    
    try:
        print("Updating company via API...")
        response = requests.put(f"{BASE_URL}/{company_id}", json=update_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Updated Company ID: {company_id}")
            print(f"New business operations: {result.get('business_operations', 'Not found')}")
            
            # Check audit logs
            print_audit_logs(company_id)
            
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def cleanup_company(company_id: int):
    """Delete test company via API"""
    print(f"\nCLEANUP")
    print("="*30)
    
    try:
        response = requests.delete(f"{BASE_URL}/{company_id}")
        if response.status_code == 200:
            print(f"Deleted company {company_id}")
        else:
            print(f"Delete error: {response.status_code}")
    except Exception as e:
        print(f"Cleanup error: {e}")

def main():
    """Test audit logging via API"""
    print("AUDIT LOGGING API TESTS")
    print("="*50)
    print("NOTE: This test requires the FastAPI server to be running!")
    print("Run: uvicorn main:app --reload --port 8000")
    print()
    
    # Test create
    company_id = test_api_create()
    if not company_id:
        print("Create test failed")
        return
        
    # Test update
    test_api_update(company_id)
    
    # Cleanup
    cleanup_company(company_id)
    
    print("\nAPI TESTS COMPLETED")

if __name__ == "__main__":
    main()