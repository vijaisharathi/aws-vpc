-- ==============================================================================
-- Master SQL Script: Complete Database Setup & Verification
-- Project: AWS VPC – Public and Private Subnet Demonstration
-- Usage: mysql -h <rds_endpoint> -u dbadmin -p < sql/init_all.sql
-- ==============================================================================

-- 1. Initialize Database
CREATE DATABASE IF NOT EXISTS academicdb
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE academicdb;

-- 2. Create Schema
CREATE TABLE IF NOT EXISTS visitors (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    visitor_name VARCHAR(100) NOT NULL,
    email        VARCHAR(150) NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Seed Sample Records
INSERT INTO visitors (visitor_name, email, created_at) VALUES
('Dr. Alan Turing', 'alan.turing@cambridge.ac.uk', NOW() - INTERVAL 5 DAY),
('Grace Hopper', 'grace.hopper@usnavy.mil', NOW() - INTERVAL 4 DAY),
('Ada Lovelace', 'ada.lovelace@science.org', NOW() - INTERVAL 3 DAY),
('Claude Shannon', 'claude.shannon@mit.edu', NOW() - INTERVAL 2 DAY),
('Margaret Hamilton', 'margaret.hamilton@mit-apollo.org', NOW() - INTERVAL 1 DAY),
('Academic Evaluator', 'evaluator@university.edu', NOW());

-- 4. Demonstration CRUD Operations
-- Perform an INSERT
INSERT INTO visitors (visitor_name, email) 
VALUES ('Cloud Architect', 'architect@aws-academic.org');

-- Perform an UPDATE
UPDATE visitors 
SET visitor_name = 'Admiral Grace Hopper'
WHERE email = 'grace.hopper@usnavy.mil';

-- 5. Final SELECT Verification Output
SELECT 
    id, 
    visitor_name, 
    email, 
    DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') AS formatted_created_at
FROM visitors
ORDER BY id ASC;

