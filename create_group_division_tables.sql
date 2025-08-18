-- Create separate tables for Groups and Divisions
-- Groups and Divisions will have basic information only

-- Create Groups table
CREATE TABLE IF NOT EXISTS groups (
    Record_ID INT AUTO_INCREMENT PRIMARY KEY,
    Group_Print_Name VARCHAR(255) NOT NULL,
    Parent_ID INT NULL,
    Legal_Name VARCHAR(255) NOT NULL,
    Other_Names TEXT NULL,
    Living_Status ENUM('Active', 'Inactive', 'Dormant', 'In Process') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (Parent_ID) REFERENCES groups(Record_ID) ON DELETE CASCADE,
    INDEX idx_parent_id (Parent_ID),
    INDEX idx_group_name (Group_Print_Name)
);

-- Create Divisions table  
CREATE TABLE IF NOT EXISTS divisions (
    Record_ID INT AUTO_INCREMENT PRIMARY KEY,
    Division_Print_Name VARCHAR(255) NOT NULL,
    Parent_ID INT NULL, -- Can belong to a group or another division
    Parent_Type ENUM('Group', 'Division') NULL, -- To know if parent is group or division
    Legal_Name VARCHAR(255) NOT NULL,
    Other_Names TEXT NULL,
    Living_Status ENUM('Active', 'Inactive', 'Dormant', 'In Process') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_parent_id (Parent_ID),
    INDEX idx_division_name (Division_Print_Name)
);

-- Keep the existing companies table as is for companies
-- Companies can have parent as Group, Division, or Company

-- Add foreign key constraints for companies table to reference groups/divisions
-- ALTER TABLE companies ADD COLUMN Parent_Type ENUM('Group', 'Division', 'Company') NULL;

-- Check tables structure
DESCRIBE groups;
DESCRIBE divisions;
DESCRIBE companies;