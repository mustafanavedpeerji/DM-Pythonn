#!/usr/bin/env python3
"""
Migration script to add missing columns to companies table
"""

import pymysql
from database import SQLALCHEMY_DATABASE_URL

def migrate_companies_table():
    """Add missing columns to companies table"""
    
    # Parse MySQL connection details
    import re
    match = re.match(r'mysql\+pymysql://([^:]+):([^@]+)@([^/]+)/(.+)', SQLALCHEMY_DATABASE_URL)
    if not match:
        print("Could not parse database URL")
        return False
    
    user, password, host, database = match.groups()
    
    # Connect to MySQL
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    
    try:
        # Check existing columns  
        cursor.execute("DESCRIBE companies")
        existing_columns = [column[0] for column in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Define new columns to add (MySQL syntax)
        new_columns = [
            ("living_status", "ENUM('Active', 'Inactive', 'Dormant', 'In Process') DEFAULT 'Active'"),
            ("ownership_type", "VARCHAR(100)"),
            ("global_operations", "ENUM('Local', 'National', 'Multi National') DEFAULT 'Local'"),
            ("founding_year", "VARCHAR(4)"),
            ("established_date", "DATE"),
            ("company_size", "INT DEFAULT 3"),
            ("ntn_no", "VARCHAR(50)"),
            ("selected_industries", "JSON"),
            ("financial_rating", "INT DEFAULT 3"),
            ("operational_rating", "INT DEFAULT 3"),
            ("compliance_rating", "INT DEFAULT 3"),
            ("market_rating", "INT DEFAULT 3"),
            ("innovation_rating", "INT DEFAULT 3")
        ]
        
        # Add missing columns
        added_columns = []
        for column_name, column_def in new_columns:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE companies ADD COLUMN {column_name} {column_def}"
                    cursor.execute(sql)
                    added_columns.append(column_name)
                    print(f"Added column: {column_name}")
                except pymysql.Error as e:
                    print(f"Error adding column {column_name}: {e}")
        
        # Commit changes
        conn.commit()
        
        if added_columns:
            print(f"Successfully added {len(added_columns)} columns: {added_columns}")
        else:
            print("No new columns needed to be added")
        
        # Verify the table structure
        cursor.execute("DESCRIBE companies")
        final_columns = [column[0] for column in cursor.fetchall()]
        print(f"Final columns: {final_columns}")
        
        return True
        
    except pymysql.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting companies table migration...")
    success = migrate_companies_table()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")