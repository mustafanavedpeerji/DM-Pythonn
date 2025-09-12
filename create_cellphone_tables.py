#!/usr/bin/env python3
"""
Create cell phone tables
"""
from sqlalchemy import create_engine
from database import SQLALCHEMY_DATABASE_URL, Base
from cell_phones.models import CellPhoneDirectory, CellPhoneAssociation

def create_tables():
    """Create cell phone tables"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    print("Creating cell phone tables...")
    # Create tables with new schema
    CellPhoneDirectory.__table__.create(engine, checkfirst=True)
    CellPhoneAssociation.__table__.create(engine, checkfirst=True)
    
    print("Cell phone tables created successfully!")

if __name__ == "__main__":
    create_tables()