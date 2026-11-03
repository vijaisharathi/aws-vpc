-- ==============================================================================
-- Script 04: Basic Operations (SELECT, INSERT, UPDATE)
-- Project: AWS VPC – Public and Private Subnet Demonstration
-- Table: visitors
-- ==============================================================================

USE academicdb;

-- -----------------------------------------------------------------------------
-- 1. SELECT Operations
-- -----------------------------------------------------------------------------

-- 1.1 Retrieve all visitors ordered by submission date (newest first)
SELECT id, visitor_name, email, created_at 
FROM visitors 
ORDER BY created_at DESC;

-- 1.2 Retrieve a specific visitor record by unique Primary Key (ID)
SELECT id, visitor_name, email, created_at 
FROM visitors 
WHERE id = 1;

-- 1.3 Search for visitors matching an email pattern
SELECT id, visitor_name, email 
FROM visitors 
WHERE email LIKE '%@university.edu';

-- 1.4 Aggregate query: Count total registered visitors
SELECT 
    COUNT(*) AS total_visitors,
    MIN(created_at) AS earliest_visit,
    MAX(created_at) AS latest_visit
FROM visitors;

-- -----------------------------------------------------------------------------
-- 2. INSERT Operations
-- -----------------------------------------------------------------------------

-- 2.1 Insert a single new visitor record
INSERT INTO visitors (visitor_name, email)
VALUES ('Kottai Kannan', 'kottai.kannan@student.ac.in');

-- 2.2 Verify the newly inserted visitor ID
SELECT * FROM visitors WHERE email = 'kottai.kannan@student.ac.in';

-- -----------------------------------------------------------------------------
-- 3. UPDATE Operations
-- -----------------------------------------------------------------------------

-- 3.1 Update an existing visitor's email address by ID
UPDATE visitors 
SET email = 'alan.turing.updated@cambridge.ac.uk'
WHERE id = 1;

-- 3.2 Update a visitor's name based on email lookup
UPDATE visitors 
SET visitor_name = 'Admiral Grace Hopper'
WHERE email = 'grace.hopper@usnavy.mil';

-- 3.3 Verify updated records
SELECT id, visitor_name, email, created_at 
FROM visitors 
WHERE id IN (1, 2);

