-- ==============================================================================
-- Script 03: Sample Records Seed Data
-- Project: AWS VPC – Public and Private Subnet Demonstration
-- Table: visitors
-- ==============================================================================

USE academicdb;

-- Insert sample demonstration records
INSERT INTO visitors (visitor_name, email, created_at) VALUES
('Dr. Alan Turing', 'alan.turing@cambridge.ac.uk', NOW() - INTERVAL 5 DAY),
('Grace Hopper', 'grace.hopper@usnavy.mil', NOW() - INTERVAL 4 DAY),
('Ada Lovelace', 'ada.lovelace@science.org', NOW() - INTERVAL 3 DAY),
('Claude Shannon', 'claude.shannon@mit.edu', NOW() - INTERVAL 2 DAY),
('Margaret Hamilton', 'margaret.hamilton@mit-apollo.org', NOW() - INTERVAL 1 DAY),
('Academic Evaluator', 'evaluator@university.edu', NOW());

-- Confirm record insertion count
SELECT COUNT(*) AS total_sample_visitors FROM visitors;

