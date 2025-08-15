-- SQL script to add missing columns to companies table
-- Run this in Navicat or your MySQL client

-- Add the missing columns to companies table
ALTER TABLE companies ADD COLUMN living_status ENUM('Active', 'Inactive', 'Dormant', 'In Process') DEFAULT 'Active';
ALTER TABLE companies ADD COLUMN ownership_type VARCHAR(100);
ALTER TABLE companies ADD COLUMN global_operations ENUM('Local', 'National', 'Multi National') DEFAULT 'Local';
ALTER TABLE companies ADD COLUMN founding_year VARCHAR(4);
ALTER TABLE companies ADD COLUMN established_date DATE;
ALTER TABLE companies ADD COLUMN company_size INT DEFAULT 3;
ALTER TABLE companies ADD COLUMN ntn_no VARCHAR(50);
ALTER TABLE companies ADD COLUMN selected_industries JSON;
ALTER TABLE companies ADD COLUMN financial_rating INT DEFAULT 3;
ALTER TABLE companies ADD COLUMN operational_rating INT DEFAULT 3;
ALTER TABLE companies ADD COLUMN compliance_rating INT DEFAULT 3;
ALTER TABLE companies ADD COLUMN market_rating INT DEFAULT 3;
ALTER TABLE companies ADD COLUMN innovation_rating INT DEFAULT 3;

-- Verify the columns were added
DESCRIBE companies;