USE team2_firmhub;

-- ================================================================
-- VIEW: vw_firm_panel_latest
-- ================================================================
-- Purpose: Return latest snapshot for each firm-year (100 rows)
-- Columns: 42 (ticker, company_name, fiscal_year, firm_id + 38 variables)
-- Logic: Select MAX(snapshot_id) for each firm-year combination
-- ================================================================

DROP VIEW IF EXISTS vw_firm_panel_latest;

CREATE VIEW vw_firm_panel_latest AS
SELECT 
    -- ============================================================
    -- Firm info (4 columns)
    -- ============================================================
    f.firm_id,
    f.ticker,
    f.company_name,
    fy.fiscal_year,
    
    -- ============================================================
    -- Ownership (4 columns)
    -- ============================================================
    own.managerial_inside_own,
    own.state_own,
    own.institutional_own,
    own.foreign_own,
    
    -- ============================================================
    -- Market (4 columns)
    -- ============================================================
    mkt.shares_outstanding,
    mkt.market_value_equity,
    mkt.dividend_cash_paid,
    mkt.eps_basic,
    
    -- ============================================================
    -- Financial (23 columns)
    -- ============================================================
    fin.net_sales,
    fin.total_assets,
    fin.selling_expenses,
    fin.general_admin_expenses,
    fin.intangible_assets_net,
    fin.manufacturing_overhead,
    fin.net_operating_income,
    fin.raw_material_consumption,
    fin.merchandise_purchase_year,
    fin.wip_goods_purchase,
    fin.outside_manufacturing_expenses,
    fin.production_cost,
    fin.rnd_expenses,
    fin.net_income,
    fin.total_equity,
    fin.total_liabilities,
    fin.cash_and_equivalents,
    fin.long_term_debt,
    fin.current_assets,
    fin.current_liabilities,
    fin.growth_ratio,
    fin.inventory,
    fin.net_ppe,
    
    -- ============================================================
    -- Cashflow (3 columns)
    -- ============================================================
    cf.net_cfo,
    cf.capex,
    cf.net_cfi,
    
    -- ============================================================
    -- Innovation (2 columns)
    -- ============================================================
    inn.product_innovation,
    inn.process_innovation,
    
    -- ============================================================
    -- Metadata (2 columns)
    -- ============================================================
    meta.employees_count,
    meta.firm_age

FROM dim_firm f

-- Cross join với all fiscal years
CROSS JOIN (
    SELECT DISTINCT fiscal_year 
    FROM fact_data_snapshot
    ORDER BY fiscal_year
) fy

-- ============================================================
-- Join với các fact tables (chọn snapshot_id lớn nhất)
-- ============================================================

-- Ownership
LEFT JOIN fact_ownership_year own ON 
    own.firm_id = f.firm_id 
    AND own.fiscal_year = fy.fiscal_year
    AND own.snapshot_id = (
        SELECT MAX(snapshot_id)
        FROM fact_ownership_year
        WHERE firm_id = f.firm_id 
          AND fiscal_year = fy.fiscal_year
    )

-- Financial
LEFT JOIN fact_financial_year fin ON 
    fin.firm_id = f.firm_id 
    AND fin.fiscal_year = fy.fiscal_year
    AND fin.snapshot_id = (
        SELECT MAX(snapshot_id)
        FROM fact_financial_year
        WHERE firm_id = f.firm_id 
          AND fiscal_year = fy.fiscal_year
    )

-- Cashflow
LEFT JOIN fact_cashflow_year cf ON 
    cf.firm_id = f.firm_id 
    AND cf.fiscal_year = fy.fiscal_year
    AND cf.snapshot_id = (
        SELECT MAX(snapshot_id)
        FROM fact_cashflow_year
        WHERE firm_id = f.firm_id 
          AND fiscal_year = fy.fiscal_year
    )

-- Market
LEFT JOIN fact_market_year mkt ON 
    mkt.firm_id = f.firm_id 
    AND mkt.fiscal_year = fy.fiscal_year
    AND mkt.snapshot_id = (
        SELECT MAX(snapshot_id)
        FROM fact_market_year
        WHERE firm_id = f.firm_id 
          AND fiscal_year = fy.fiscal_year
    )

-- Innovation
LEFT JOIN fact_innovation_year inn ON 
    inn.firm_id = f.firm_id 
    AND inn.fiscal_year = fy.fiscal_year
    AND inn.snapshot_id = (
        SELECT MAX(snapshot_id)
        FROM fact_innovation_year
        WHERE firm_id = f.firm_id 
          AND fiscal_year = fy.fiscal_year
    )

-- Metadata
LEFT JOIN fact_firm_year_meta meta ON 
    meta.firm_id = f.firm_id 
    AND meta.fiscal_year = fy.fiscal_year
    AND meta.snapshot_id = (
        SELECT MAX(snapshot_id)
        FROM fact_firm_year_meta
        WHERE firm_id = f.firm_id 
          AND fiscal_year = fy.fiscal_year
    )

ORDER BY f.ticker, fy.fiscal_year;

-- ================================================================
-- END OF VIEWS
-- ================================================================

SELECT '✓ View vw_firm_panel_latest created successfully' as status;