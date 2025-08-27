-- Create audit_logs table for comprehensive field-level tracking
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(50) NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    action_type ENUM('CREATE', 'UPDATE', 'DELETE') NOT NULL,
    old_value TEXT NULL,
    new_value TEXT NULL,
    user_id VARCHAR(100) NULL,
    user_name VARCHAR(255) NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for better performance
    INDEX idx_table_record (table_name, record_id),
    INDEX idx_action_type (action_type),
    INDEX idx_timestamp (timestamp),
    INDEX idx_user (user_id),
    INDEX idx_field (field_name)
);

-- Verify table creation
DESCRIBE audit_logs;