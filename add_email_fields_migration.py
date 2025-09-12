#!/usr/bin/env python3
"""
Database migration script to add gender and city fields to email_directory table
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'business_management')
        )
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def add_email_fields():
    """Add gender and city fields to email_directory table"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Check if fields already exist
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'email_directory' 
            AND COLUMN_NAME IN ('gender', 'city')
        """, (os.getenv('MYSQL_DATABASE', 'business_management'),))
        
        existing_fields = [row[0] for row in cursor.fetchall()]
        
        # Add gender field if it doesn't exist
        if 'gender' not in existing_fields:
            print("Adding gender field to email_directory table...")
            cursor.execute("""
                ALTER TABLE email_directory 
                ADD COLUMN gender VARCHAR(10) NULL 
                COMMENT 'Gender: Male, Female, Unknown'
            """)
            print("✓ Gender field added successfully")
        else:
            print("✓ Gender field already exists")
        
        # Add city field if it doesn't exist
        if 'city' not in existing_fields:
            print("Adding city field to email_directory table...")
            cursor.execute("""
                ALTER TABLE email_directory 
                ADD COLUMN city VARCHAR(100) NULL 
                COMMENT 'City in Pakistan'
            """)
            print("✓ City field added successfully")
        else:
            print("✓ City field already exists")
        
        connection.commit()
        return True
        
    except Error as e:
        print(f"Error executing migration: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("Starting email_directory table migration...")
    success = add_email_fields()
    if success:
        print("\n✅ Migration completed successfully!")
        print("New fields added to email_directory:")
        print("- gender VARCHAR(10) NULL")
        print("- city VARCHAR(100) NULL")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above and try again.")