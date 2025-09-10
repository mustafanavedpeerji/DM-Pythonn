#!/usr/bin/env python3
"""
Recreate email tables with the new schema
"""
from sqlalchemy import create_engine
from database import SQLALCHEMY_DATABASE_URL, Base
from emails.models import EmailDirectory, EmailAssociation

def recreate_tables():
    """Drop and recreate email tables"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    print("Dropping existing email tables...")
    # Drop tables in correct order (associations first due to foreign key)
    EmailAssociation.__table__.drop(engine, checkfirst=True)
    EmailDirectory.__table__.drop(engine, checkfirst=True)
    
    print("Creating new email tables with updated schema...")
    # Create tables with new schema
    EmailDirectory.__table__.create(engine, checkfirst=True)
    EmailAssociation.__table__.create(engine, checkfirst=True)
    
    print("Tables recreated successfully!")

if __name__ == "__main__":
    recreate_tables()