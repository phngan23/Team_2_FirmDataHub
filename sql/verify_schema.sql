-- ================================================================
-- DATABASE VERIFICATION SCRIPT
-- Vietnamese Firm Panel Database
-- ================================================================
-- Purpose: Verify schema setup and data counts
-- Run after: schema_and_seed.sql
-- ================================================================

USE vn_firm_panel;

-- Show database info
SELECT DATABASE() as current_database, 
       @@character_set_database as charset, 
       @@collation_database as collation;

-- ================================================================
-- TABLE EXISTENCE CHECK
-- ================================================================
SELECT 
    TABLE_NAME,
    TABLE_TYPE,
    ENGINE,
    TABLE_ROWS,
    TABLE_COMMENT
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'vn_firm_panel'
ORDER BY 
    CASE 
        WHEN TABLE_NAME LIKE 'dim_%' THEN 1
        WHEN TABLE_NAME LIKE 'fact_%' THEN 2
        ELSE 3
    END,
    TABLE_NAME;

-- ================================================================
-- ROW COUNT VERIFICATION
-- ================================================================
SELECT 'dim_data_source' as table_name, COUNT(*) as actual, 4 as expected FROM dim_data_source
UNION ALL
SELECT 'dim_exchange', COUNT(*), 2 FROM dim_exchange
UNION ALL
SELECT 'dim_industry_l2', COUNT(*), 9 FROM dim_industry_l2
UNION ALL
SELECT 'dim_firm', COUNT(*), 0 FROM dim_firm
UNION ALL
SELECT 'fact_data_snapshot', COUNT(*), 20 FROM fact_data_snapshot
UNION ALL
SELECT 'fact_financial_year', COUNT(*), 0 FROM fact_financial_year
UNION ALL
SELECT 'fact_cashflow_year', COUNT(*), 0 FROM fact_cashflow_year
UNION ALL
SELECT 'fact_market_year', COUNT(*), 0 FROM fact_market_year
UNION ALL
SELECT 'fact_ownership_year', COUNT(*), 0 FROM fact_ownership_year
UNION ALL
SELECT 'fact_innovation_year', COUNT(*), 0 FROM fact_innovation_year
UNION ALL
SELECT 'fact_firm_year_meta', COUNT(*), 0 FROM fact_firm_year_meta;

-- ================================================================
-- FOREIGN KEY VERIFICATION
-- ================================================================
SELECT 
    CONSTRAINT_NAME,
    TABLE_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'vn_firm_panel'
    AND REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY TABLE_NAME, CONSTRAINT_NAME;

-- ================================================================
-- MASTER DATA VERIFICATION
-- ================================================================

-- Check data sources
SELECT 'Data Sources:' as info;
SELECT source_id, source_name, source_type FROM dim_data_source ORDER BY source_id;

-- Check exchanges
SELECT 'Exchanges:' as info;
SELECT exchange_id, exchange_code, exchange_name FROM dim_exchange ORDER BY exchange_id;

-- Check industries
SELECT 'Industries:' as info;
SELECT industry_l2_id, industry_l2_name FROM dim_industry_l2 ORDER BY industry_l2_id;

-- Check snapshots
SELECT 'Snapshots (first 5):' as info;
SELECT snapshot_id, fiscal_year, source_id, snapshot_date 
FROM fact_data_snapshot 
ORDER BY fiscal_year, source_id 
LIMIT 5;

-- ================================================================
-- SUMMARY
-- ================================================================
SELECT 
    CONCAT('✅ Schema created successfully!') as status,
    (SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'vn_firm_panel') as total_tables,
    (SELECT COUNT(*) FROM dim_data_source) + 
    (SELECT COUNT(*) FROM dim_exchange) + 
    (SELECT COUNT(*) FROM dim_industry_l2) + 
    (SELECT COUNT(*) FROM fact_data_snapshot) as total_seed_records;

-- ================================================================
-- NEXT STEPS
-- ================================================================
-- After verification passes:
-- 1. Run import_panel.py to load Excel data
-- 2. Run verify_data.sql to check imported data
-- ================================================================