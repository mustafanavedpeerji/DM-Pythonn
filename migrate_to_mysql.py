#!/usr/bin/env python3
"""
Fixed SQLite to MySQL Migration Script for Industries Database
Handles data integrity issues with parent_id references
"""

import sqlite3
import pymysql
import sys
import os

def analyze_data():
    """Analyze the SQLite data for issues"""
    print("🔍 Analyzing SQLite data for issues...")
    
    sqlite_conn = sqlite3.connect('industries.db')
    cursor = sqlite_conn.cursor()
    
    # Get all records
    cursor.execute("SELECT id, industry_name, category, parent_id FROM industries ORDER BY id")
    all_records = cursor.fetchall()
    
    # Get all existing IDs
    existing_ids = {record[0] for record in all_records}
    
    # Find orphaned records (parent_id doesn't exist)
    orphaned_records = []
    valid_records = []
    
    for record in all_records:
        record_id, name, category, parent_id = record
        if parent_id is not None and parent_id not in existing_ids:
            orphaned_records.append(record)
            print(f"❌ Orphaned: ID {record_id} '{name}' references non-existent parent {parent_id}")
        else:
            valid_records.append(record)
    
    print(f"📊 Total records: {len(all_records)}")
    print(f"✅ Valid records: {len(valid_records)}")
    print(f"❌ Orphaned records: {len(orphaned_records)}")
    
    sqlite_conn.close()
    return valid_records, orphaned_records

def fix_orphaned_records():
    """Fix orphaned records by setting their parent_id to NULL"""
    print("\n🔧 Fixing orphaned records...")
    
    sqlite_conn = sqlite3.connect('industries.db')
    cursor = sqlite_conn.cursor()
    
    # Fix records with parent_id = 0 (set to NULL)
    cursor.execute("UPDATE industries SET parent_id = NULL WHERE parent_id = 0")
    affected = cursor.rowcount
    print(f"✅ Fixed {affected} records with parent_id = 0 (set to NULL)")
    
    # Get all existing IDs
    cursor.execute("SELECT id FROM industries")
    existing_ids = {row[0] for row in cursor.fetchall()}
    
    # Fix other orphaned records
    cursor.execute("SELECT id, industry_name, parent_id FROM industries WHERE parent_id IS NOT NULL")
    records = cursor.fetchall()
    
    fixed_count = 0
    for record_id, name, parent_id in records:
        if parent_id not in existing_ids:
            cursor.execute("UPDATE industries SET parent_id = NULL WHERE id = ?", (record_id,))
            fixed_count += 1
            print(f"✅ Fixed ID {record_id} '{name}': removed invalid parent_id {parent_id}")
    
    sqlite_conn.commit()
    sqlite_conn.close()
    
    print(f"🔧 Total orphaned records fixed: {fixed_count + affected}")
    return True

def migrate_data():
    """Migrate data from SQLite to MySQL with proper ordering"""
    
    # MySQL connection settings - UPDATE THESE WITH YOUR CREDENTIALS
    MYSQL_CONFIG = {
        'host': 'localhost',
        'user': 'magicfin_industries',  # Update if different
        'password': 'magicfin_industries',  # ⚠️ REPLACE THIS
        'database': 'magicfin_industries',  # Update if different
        'charset': 'utf8mb4'
    }
    
    try:
        print("🔄 Starting migration from SQLite to MySQL...")
        
        # Connect to SQLite
        print("📂 Connecting to SQLite database...")
        sqlite_conn = sqlite3.connect('industries.db')
        sqlite_cursor = sqlite_conn.cursor()
        
        # Get all data from SQLite (after fixes)
        sqlite_cursor.execute("SELECT id, industry_name, category, parent_id FROM industries ORDER BY id")
        industries_data = sqlite_cursor.fetchall()
        print(f"📊 Found {len(industries_data)} records in SQLite")
        
        # Connect to MySQL
        print("🔗 Connecting to MySQL database...")
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        mysql_cursor = mysql_conn.cursor()
        
        # Clear existing data
        print("🧹 Clearing existing data in MySQL...")
        mysql_cursor.execute("SET foreign_key_checks = 0")
        mysql_cursor.execute("DELETE FROM industries")
        mysql_cursor.execute("ALTER TABLE industries AUTO_INCREMENT = 1")
        mysql_cursor.execute("SET foreign_key_checks = 1")
        
        # Insert data in proper order
        print("📥 Inserting data into MySQL...")
        insert_query = "INSERT INTO industries (id, industry_name, category, parent_id) VALUES (%s, %s, %s, %s)"
        
        # Separate root records from child records
        root_records = [record for record in industries_data if record[3] is None]
        child_records = [record for record in industries_data if record[3] is not None]
        
        print(f"📥 Inserting {len(root_records)} root records...")
        success_count = 0
        
        # Insert root records first
        for record in root_records:
            try:
                mysql_cursor.execute(insert_query, record)
                success_count += 1
                print(f"✅ Root: ID {record[0]} - {record[1]}")
            except Exception as e:
                print(f"❌ Error inserting root record {record[0]}: {e}")
        
        mysql_conn.commit()
        
        # Insert child records in multiple passes
        print(f"📥 Inserting {len(child_records)} child records...")
        remaining_records = child_records.copy()
        max_attempts = 5
        attempt = 1
        
        while remaining_records and attempt <= max_attempts:
            print(f"📥 Attempt {attempt} - {len(remaining_records)} records remaining...")
            failed_records = []
            
            for record in remaining_records:
                try:
                    mysql_cursor.execute(insert_query, record)
                    success_count += 1
                    print(f"✅ Child: ID {record[0]} - {record[1]} (parent: {record[3]})")
                except Exception as e:
                    failed_records.append(record)
            
            mysql_conn.commit()
            remaining_records = failed_records
            attempt += 1
        
        # Report results
        if remaining_records:
            print(f"❌ Failed to insert {len(remaining_records)} records:")
            for record in remaining_records:
                print(f"   - ID {record[0]}: {record[1]} (parent: {record[3]})")
        
        print(f"✅ Successfully migrated {success_count} out of {len(industries_data)} records")
        
        # Verify data
        mysql_cursor.execute("SELECT COUNT(*) FROM industries")
        mysql_count = mysql_cursor.fetchone()[0]
        print(f"🔍 Verification: MySQL now contains {mysql_count} records")
        
        # Close connections
        sqlite_conn.close()
        mysql_conn.close()
        
        print("🎉 Migration completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Fixed Industries Database Migration Tool")
    print("=" * 60)
    
    # Step 1: Analyze current data
    valid_records, orphaned_records = analyze_data()
    
    if orphaned_records:
        print(f"\n⚠️ Found {len(orphaned_records)} orphaned records that need fixing.")
        response = input("Do you want to fix these records automatically? (y/n): ").lower().strip()
        
        if response == 'y':
            fix_orphaned_records()
            print("✅ Data integrity issues fixed!")
        else:
            print("❌ Cannot proceed with orphaned records. Migration aborted.")
            sys.exit(1)
    
    # Step 2: Run migration
    print("\n" + "=" * 40)
    print("🚀 Starting Migration Process")
    print("=" * 40)
    
    if migrate_data():
        print("\n🎊 Migration completed successfully!")
        print("\nNext steps:")
        print("1. ✅ Update your database.py file")
        print("2. ✅ Update your models.py file")
        print("3. ✅ Test your FastAPI application")
        print("4. ✅ Check your data in phpMyAdmin")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
        sys.exit(1)