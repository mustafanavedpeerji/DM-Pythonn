#!/usr/bin/env python3
"""
Script to update existing age bracket values from old format to new format
"""

from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def fix_age_brackets():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    age_bracket_mapping = {
        'Young Adult (20-30)': '20-30',
        'Adult (30-40)': '30-40', 
        'Middle-aged (40-50)': '40-50',
        'Middle-aged (50-60)': '50-60',
        'Senior (60-70)': '60-70',
        'Senior (70-80)': '70-80',
        'Elderly (80-90)': '80-90',
        'Child (0-12)': None,  # Set to NULL for children
        'Teen (12-20)': None,  # Set to NULL for teens
        'Very Elderly (90+)': None,  # Set to NULL for very elderly
    }
    
    with engine.connect() as connection:
        # First, let's see what values exist
        result = connection.execute(text("SELECT DISTINCT age_bracket FROM persons WHERE age_bracket IS NOT NULL"))
        existing_values = [row[0] for row in result.fetchall()]
        print(f"Found existing age bracket values: {existing_values}")
        
        # Update each mapping
        for old_value, new_value in age_bracket_mapping.items():
            if old_value in existing_values:
                if new_value is None:
                    # Set to NULL
                    result = connection.execute(
                        text("UPDATE persons SET age_bracket = NULL WHERE age_bracket = :old_value"),
                        {"old_value": old_value}
                    )
                else:
                    # Update to new value
                    result = connection.execute(
                        text("UPDATE persons SET age_bracket = :new_value WHERE age_bracket = :old_value"),
                        {"old_value": old_value, "new_value": new_value}
                    )
                print(f"Updated {result.rowcount} rows: '{old_value}' -> '{new_value}'")
        
        # Commit the changes
        connection.commit()
        
        # Verify the results
        result = connection.execute(text("SELECT DISTINCT age_bracket FROM persons WHERE age_bracket IS NOT NULL"))
        final_values = [row[0] for row in result.fetchall()]
        print(f"Final age bracket values: {final_values}")

if __name__ == "__main__":
    fix_age_brackets()
    print("Age bracket fix completed!")