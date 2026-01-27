/*
schema_and_seed.sql

Purpose
-------
Create all DIM, FACT, SNAPSHOT tables and views
Define the database schema and seed initial data for the Firm Data Hub.

Main Responsibilities
---------------------
- Create all required DIM tables:
    + dim_firm
    + dim_exchange
    + dim_industry_l2
    + dim_data_source
- Create FACT tables with snapshot-based versioning
- Define primary keys, foreign keys, and constraints
- Create required analytical views:
    + vw_firm_panel_latest
- Insert minimal seed data for testing and initialization

-- TODO:
-- 1. Create dim_exchange
-- 2. Create dim_industry_l2
-- 3. Create dim_firm
-- 4. Create fact_data_snapshot
-- 5. Create FACT tables
-- 6. Create view vw_firm_panel_latest

Notes
-----
- Script must be idempotent
- Designed to allow full database recreation
*/
