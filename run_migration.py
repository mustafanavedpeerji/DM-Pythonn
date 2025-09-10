#!/usr/bin/env python3
"""
Run database migration script to update email_associations table
"""
import pymysql
import sys
import os

# Database configuration
DB_HOST = "magicfingers.com.pk"
DB_USER = "magicfin_industries"  
DB_PASSWORD = "magicfin_industries"
DB_NAME = "magicfin_industries"

def run_migration():
    """Execute the migration SQL script"""
    try:
        # Connect to database
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection:
            cursor = connection.cursor()
            
            # Check if migration has already been run
            cursor.execute("SHOW COLUMNS FROM email_associations LIKE 'departments'")
            if cursor.fetchone():
                print("Migration already appears to be run - departments column exists.")
                return
            
            # Read the migration file
            migration_file = os.path.join(os.path.dirname(__file__), 'migrations', 'update_email_associations.sql')
            with open(migration_file, 'r') as f:
                sql_content = f.read()
            
            # Split into individual statements and execute
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
            
            for i, statement in enumerate(statements):
                if statement:
                    print(f"Executing statement {i+1}/{len(statements)}")
                    print(f"SQL: {statement[:100]}...")
                    try:
                        cursor.execute(statement)
                        connection.commit()
                        print("✓ Success")
                    except Exception as e:
                        print(f"✗ Error: {e}")
                        # Continue with other statements
                        connection.rollback()
            
            print("\nMigration completed!")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()