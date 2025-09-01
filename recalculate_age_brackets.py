#!/usr/bin/env python3
"""
Script to recalculate age brackets for all persons
"""

from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL
from datetime import date

def calculate_age_bracket(birth_date):
    """Calculate age bracket based on birth date"""
    if not birth_date:
        return None
        
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    if age < 20:
        return None
    elif age <= 30:
        return "20-30"
    elif age <= 40:
        return "30-40"
    elif age <= 50:
        return "40-50"
    elif age <= 60:
        return "50-60"
    elif age <= 70:
        return "60-70"
    elif age <= 80:
        return "70-80"
    elif age <= 90:
        return "80-90"
    else:
        return None

def recalculate_age_brackets():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as connection:
        # Get all persons with date of birth
        result = connection.execute(text("SELECT record_id, date_of_birth FROM persons WHERE date_of_birth IS NOT NULL"))
        persons = result.fetchall()
        
        print(f"Found {len(persons)} persons with date_of_birth")
        
        updated_count = 0
        for record_id, date_of_birth in persons:
            calculated_age_bracket = calculate_age_bracket(date_of_birth)
            print(f"Person {record_id}: DOB={date_of_birth}, calculated age_bracket={calculated_age_bracket}")
            
            # Update the age bracket
            connection.execute(
                text("UPDATE persons SET age_bracket = :age_bracket WHERE record_id = :record_id"),
                {"age_bracket": calculated_age_bracket, "record_id": record_id}
            )
            updated_count += 1
        
        # Also clean up any remaining empty strings
        result = connection.execute(text("UPDATE persons SET age_bracket = NULL WHERE age_bracket = ''"))
        empty_fixed = result.rowcount
        
        connection.commit()
        print(f"Updated {updated_count} persons with calculated age brackets")
        print(f"Fixed {empty_fixed} empty string age brackets")
        
        # Verify results
        result = connection.execute(text("SELECT DISTINCT age_bracket FROM persons"))
        final_values = [row[0] for row in result.fetchall()]
        print(f"Final age bracket values: {final_values}")

if __name__ == "__main__":
    recalculate_age_brackets()
    print("Age bracket recalculation completed!")