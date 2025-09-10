-- Migration to update email_associations table
-- 1. Remove association_type and notes columns
-- 2. Change department column to departments (JSON array)
-- 3. Consolidate existing data to avoid multiple rows for same company

-- Step 1: Create new departments column as JSON
ALTER TABLE email_associations 
ADD COLUMN departments JSON NULL AFTER department;

-- Step 2: Migrate existing department data to departments JSON array
-- Convert single department values to JSON arrays
UPDATE email_associations 
SET departments = JSON_ARRAY(department) 
WHERE department IS NOT NULL;

-- Step 3: Consolidate multiple rows for same email+company combination
-- This is a complex operation that needs to be done carefully

-- Create temporary table to hold consolidated data
CREATE TEMPORARY TABLE temp_consolidated_associations AS
SELECT 
    email_id,
    company_id,
    person_id,
    JSON_ARRAYAGG(department) as consolidated_departments,
    MIN(association_id) as keep_id,
    MIN(created_at) as created_at
FROM email_associations 
WHERE company_id IS NOT NULL AND department IS NOT NULL
GROUP BY email_id, company_id, person_id
HAVING COUNT(*) > 1;

-- Update the associations we want to keep with consolidated departments
UPDATE email_associations ea
INNER JOIN temp_consolidated_associations tca ON ea.association_id = tca.keep_id
SET ea.departments = tca.consolidated_departments;

-- Delete duplicate associations (keep only the first one for each email+company combination)
DELETE ea1 FROM email_associations ea1
INNER JOIN temp_consolidated_associations tca ON ea1.email_id = tca.email_id 
    AND ea1.company_id = tca.company_id 
    AND (ea1.person_id = tca.person_id OR (ea1.person_id IS NULL AND tca.person_id IS NULL))
    AND ea1.association_id > tca.keep_id;

-- Step 4: Drop old columns
ALTER TABLE email_associations 
DROP COLUMN department,
DROP COLUMN association_type,
DROP COLUMN notes;

-- Step 5: Add index on departments for better query performance (if MySQL 8.0+)
-- Note: This is optional and may not work on older MySQL versions
-- ALTER TABLE email_associations ADD INDEX idx_departments ((CAST(departments AS CHAR(255) ARRAY)));