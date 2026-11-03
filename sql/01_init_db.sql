-- ==============================================================================
-- Script 01: Database Initialization
-- Project: AWS VPC – Public and Private Subnet Demonstration
-- ==============================================================================

-- Create database if it does not already exist
CREATE DATABASE IF NOT EXISTS academicdb
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Switch to the target academic database
USE academicdb;

-- Display current active database and connection character set
SELECT 
    DATABASE() AS active_database,
    @@character_set_database AS charset,
    @@collation_database AS collation;

