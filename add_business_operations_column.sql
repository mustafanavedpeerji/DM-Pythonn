-- Add business_operations column to companies table
-- This is a safe migration that adds the column without dropping existing ones

-- First check if column exists
SELECT COLUMN_NAME 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'companies' AND COLUMN_NAME = 'business_operations';

-- Add the column if it doesn't exist
ALTER TABLE companies ADD COLUMN IF NOT EXISTS business_operations TEXT;

-- Verify the column was added
DESCRIBE companies;