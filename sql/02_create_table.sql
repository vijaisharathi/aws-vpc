-- ==============================================================================
-- Script 02: Table Schema Definition
-- Project: AWS VPC – Public and Private Subnet Demonstration
-- Table: visitors
-- ==============================================================================

USE academicdb;

-- Drop table if recreation is needed during fresh testing
-- DROP TABLE IF EXISTS visitors;

CREATE TABLE IF NOT EXISTS visitors (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    visitor_name VARCHAR(100) NOT NULL,
    email        VARCHAR(150) NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Verify table creation and column structure
DESCRIBE visitors;

