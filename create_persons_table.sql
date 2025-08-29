-- Create persons table
-- Run this SQL script in your MySQL database

CREATE TABLE IF NOT EXISTS persons (
    Record_ID INT AUTO_INCREMENT PRIMARY KEY,
    person_print_name VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    gender ENUM('Male', 'Female') NOT NULL,
    living_status ENUM('Active', 'Dead', 'Missing') DEFAULT 'Active',
    professional_status ENUM('Professional', 'Retired', 'Student', 'Disabled', 'Missing', 'Unemployed') NULL,
    religion ENUM('Islam', 'Hindu', 'Christian', 'Persian', 'Sikh', 'Buddhist', 'Other', 'Unknown') NULL,
    community ENUM('Delhi', 'Memon', 'Bohri', 'Punjabi', 'Sindhi', 'Baloch', 'Pathan', 'Unknown', 'Other') NULL,
    base_city VARCHAR(100) NULL,
    birth_city VARCHAR(100) NULL,
    date_of_birth DATE NULL,
    age_bracket ENUM('Child (0-12)', 'Teen (13-19)', 'Young Adult (20-30)', 'Adult (31-50)', 'Middle Age (51-65)', 'Senior (65+)') NULL,
    nic VARCHAR(20) NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Add indexes for better performance
CREATE INDEX idx_persons_nic ON persons(nic);
CREATE INDEX idx_persons_base_city ON persons(base_city);
CREATE INDEX idx_persons_birth_city ON persons(birth_city);
CREATE INDEX idx_persons_community ON persons(community);
CREATE INDEX idx_persons_living_status ON persons(living_status);

-- Show table structure
DESCRIBE persons;