-- Update persons table: remove birth_city, add company attachment, department and designation

-- Step 1: Add new columns
ALTER TABLE persons ADD COLUMN attached_companies JSON;
ALTER TABLE persons ADD COLUMN department VARCHAR(100);
ALTER TABLE persons ADD COLUMN designation VARCHAR(100);

-- Step 2: Drop birth_city column
ALTER TABLE persons DROP COLUMN IF EXISTS birth_city;

-- Verify the changes
DESCRIBE persons;