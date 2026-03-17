## 1. Project Overview

This dataset comprises a comprehensive panel of listed firms in Vietnam over the period 2020-2025. The data is collected from multiple sources including audited financial statements, annual reports, market data providers, and ownership disclosure reports. It is designed to support academic research in corporate finance, innovation economics, and ownership structure analysis.

The database follows a data warehouse architecture with dimension and fact tables, enabling version control through snapshots, historical tracking with consistent firm identifiers, and multi-source integration of financial, market, ownership, and innovation data by firm-year-snapshot.

Key variables include financial statement items (income statement, balance sheet, cash flow), market performance indicators, ownership structure (state, foreign, institutional, managerial ownership), and innovation dummies (product/process innovation) coded from annual reports. The panel structure allows for longitudinal analysis of firm behavior, performance trends, and the impact of ownership and innovation on corporate outcomes during Vietnam's economic development from 2020 to 2025.

## 2. Table Listing

| Table Name | Type | Description |
|------------|------|-------------|
| dim_data_source | DIM | Data source master list (FiinPro, Vietstock, BCTC, AnnualReport...) |
| dim_exchange | DIM | Exchange master data (HOSE, HNX) |
| dim_industry_l2 | DIM | Industry L2 master list |
| dim_firm | DIM | Firm master list (ticker/company/exchange/industry) |
| fact_data_snapshot | FACT | Versioning ledger: each ETL batch for a source+year+version |
| fact_financial_year | FACT | Financial statement data per firm-year per snapshot |
| fact_cashflow_year | FACT | Cashflow data per firm-year per snapshot |
| fact_market_year | FACT | Market variables per firm-year per snapshot |
| fact_ownership_year | FACT | Ownership ratios per firm-year per snapshot |
| fact_innovation_year | FACT | Innovation dummy variables per firm-year per snapshot |
| fact_firm_year_meta | FACT | Employees and firm age per firm-year per snapshot |
| fact_value_override_log | AUDIT | Audit log for manual overrides/corrections |

## 3. Table Structures

### dim_data_source

| Column Name | Data Type | Nullable | Key | Description | Source/Rule |
|-------------|-----------|----------|-----|-------------|-------------|
| source_id | smallint | NO | PK | Unique identifier for each data source | Auto increment |
| source_name | varchar(100) | NO | UQ | Short name of the data source/provider | Reference list |
| source_type | enum | NO | | Category of data source | market, financial_statement, ownership, text_report, manual |
| provider | varchar(50) | YES | | Organization that provides the data | Reference |
| note | varchar(255) | YES | | Additional notes about the source | Reference |

### dim_exchange

| Column Name | Data Type | Nullable | Key | Description | Source/Rule |
|-------------|-----------|----------|-----|-------------|-------------|
| exchange_id | tinyint | NO | PK | Unique identifier for stock exchange | Auto increment |
| exchange_code | varchar(10) | NO | UQ | Official exchange code | From Excel 'San' column |
| exchange_name | varchar(100) | YES | | Full name of the exchange | Reference list |

### dim_industry_l2

| Column Name | Data Type | Nullable | Key | Description | Source/Rule |
|-------------|-----------|----------|-----|-------------|-------------|
| industry_l2_id | smallint | NO | PK | Unique identifier for industry level 2 | Auto increment |
| industry_l2_name | varchar(150) | NO | UQ | Name of the industry at level 2 | From Excel 'Nganh L2' column |

### dim_firm

| Column Name | Data Type | Nullable | Key | Description | Source/Rule |
|-------------|-----------|----------|-----|-------------|-------------|
| firm_id | bigint | NO | PK | Unique identifier for each firm | Auto increment |
| ticker | varchar(20) | NO | UQ | Stock ticker symbol | From Excel 'Ma CK' column |
| company_name | varchar(255) | NO | | Legal name of the company | From Excel 'Ten cong ty' column |
| exchange_id | tinyint | NO | FK | Exchange where the firm is listed | FK -> dim_exchange(exchange_id) |
| industry_l2_id | smallint | YES | FK | Industry classification at level 2 | FK -> dim_industry_l2(industry_l2_id) |
| founded_year | smallint | YES | | Year the company was established | Manual / company profile |
| listed_year | smallint | YES | | Year the company went public | Manual / exchange profile |
| status | enum | YES | | Current listing status | 'active', 'delisted', 'inactive' |
| created_at | timestamp | YES | | Timestamp when record was created | Auto |
| updated_at | timestamp | YES | | Timestamp when record was last updated | Auto on update |

### fact_data_snapshot

| Column Name | Data Type | Nullable | Key | Description | Source/Rule |
|-------------|-----------|----------|-----|-------------|-------------|
| snapshot_id | bigint | NO | PK | Unique identifier for each data snapshot | Auto increment |
| snapshot_date | date | NO | | Date when the data was captured/confirmed | ETL batch date / disclosure date |
| period_from | date | YES | | Start date of the reporting period (if applicable) | Optional |
| period_to | date | YES | | End date of the reporting period (if applicable) | Optional |
| fiscal_year | smallint | NO | | Fiscal year that the data corresponds to | Derived from ETL context |
| source_id | smallint | NO | FK | Source from which this snapshot was derived | FK -> dim_data_source(source_id) |
| version_tag | varchar(50) | YES | | Version identifier (v1, restated, v2, etc.) | ETL version control |
| created_by | varchar(80) | YES | | User/system that created the snapshot | ETL user/bot |
| created_at | timestamp | YES | | Timestamp when snapshot was created | Auto |

### fact_financial_year

| Column Name | Data Type | Nullable | Key | Description | Source/Rule |
|-------------|-----------|----------|-----|-------------|-------------|
| firm_id | bigint | NO | PK, FK | Firm identifier | FK -> dim_firm(firm_id) |
| fiscal_year | smallint | NO | PK | Fiscal year | Year column in panel |
| snapshot_id | bigint | NO | PK, FK | Snapshot/version link | FK -> fact_data_snapshot(snapshot_id) |
| unit_scale | bigint | NO | | Scale multiplier for monetary fields (1e9 = billion VND) | ETL configuration |
| currency_code | char(3) | NO | | Currency in which values are reported | Default VND |
| net_sales | decimal(20,2) | YES | | Net sales revenue | BCTC P&L 'Doanh thu thuan' |
| total_assets | decimal(20,2) | YES | | Book value of total assets | BCTC Balance Sheet |
| selling_expenses | decimal(20,2) | YES | | Selling expenses | BCTC P&L / notes |
| general_admin_expenses | decimal(20,2) | YES | | General & admin expenses | BCTC P&L / notes |
| intangible_assets_net | decimal(20,2) | YES | | Net intangible assets (book value) | BCTC Balance Sheet |
| manufacturing_overhead | decimal(20,2) | YES | | Indirect manufacturing overhead | Computed or from cost notes |
| net_operating_income | decimal(20,2) | YES | | Operating income before tax & depreciation | Computed / defined by study |
| raw_material_consumption | decimal(20,2) | YES | | Raw material consumption | Cost notes |
| merchandise_purchase_year | decimal(20,2) | YES | | Merchandise purchases in year | Cost notes |
| wip_goods_purchase | decimal(20,2) | YES | | Work-in-progress goods purchases | Cost notes |
| outside_manufacturing_expenses | decimal(20,2) | YES | | Outsourced manufacturing expenses | Cost notes |
| production_cost | decimal(20,2) | YES | | Total production cost (sum of 5 elements if available) | Cost notes / computed |
| rnd_expenses | decimal(20,2) | YES | | R&D expenditure | P&L / notes |
| net_income | decimal(20,2) | YES | | Net income (research definition as provided) | BCTC P&L / research mapping |
| total_equity | decimal(20,2) | YES | | Total shareholders' equity (book value) | BCTC Balance Sheet |
| total_liabilities | decimal(20,2) | YES | | Total liabilities | BCTC Balance Sheet |
| cash_and_equivalents | decimal(20,2) | YES | | Cash & cash equivalents | BCTC Balance Sheet |
| long_term_debt | decimal(20,2) | YES | | Long-term debt (>1 year) | BCTC notes / Balance Sheet |
| current_assets | decimal(20,2) | YES | | Current assets | BCTC Balance Sheet |
| current_liabilities | decimal(20,2) | YES | | Current liabilities | BCTC Balance Sheet |
| growth_ratio | decimal(10,6) | YES | | Growth ratio vs prior year (research definition) | Computed or per study |
| inventory | decimal(20,2) | YES | | Total inventory (within current assets) | BCTC Balance Sheet |
| net_ppe | decimal(20,2) | YES | | Net property, plant and equipment | BCTC Balance Sheet |
| created_at | timestamp | YES | | Row creation timestamp | Auto |

### fact_cashflow_year

| Column Name | Data Type | Nullable | Key | Description | Source/Rule |
|-------------|-----------|----------|-----|-------------|-------------|
| firm_id | bigint | NO | PK, FK | Firm identifier | FK -> dim_firm(firm_id) |
| fiscal_year | smallint | NO | PK | Fiscal year | Year column in panel |
| snapshot_id | bigint | NO | PK, FK | Snapshot/version link | FK -> fact_data_snapshot(snapshot_id) |
| unit_scale | bigint | NO | | Scale multiplier for monetary fields | Same scale as financial for consistency |
| currency_code | char(3) | NO | | Currency code | Default VND |
| net_cfo | decimal(20,2) | YES | | Net cash from operating activities | Cashflow statement |
| capex | decimal(20,2) | YES | | Capital expenditure | Cashflow statement / notes |
| net_cfi | decimal(20,2) | YES | | Cash flows from investing activities | Cashflow statement |
| created_at | timestamp | YES | | Row creation timestamp | Auto |

### fact_market_year

| Column Name | Data Type | Nullable | Key | Description | Source/Rule |
|-------------|-----------|----------|-----|-------------|-------------|
| firm_id | bigint | NO | PK, FK | Firm identifier | FK -> dim_firm(firm_id) |
| fiscal_year | smallint | NO | PK | Fiscal year | Year column in panel |
| snapshot_id | bigint | NO | PK, FK | Snapshot/version link | FK -> fact_data_snapshot(snapshot_id) |
| shares_outstanding | bigint | YES | | Total shares outstanding | Market data provider |
| price_reference | enum | YES | | How share_price was chosen | close_year_end, avg_year, close_fiscal_end |
| share_price | decimal(20,4) | YES | | Year reference share price | Market data provider |
| market_value_equity | decimal(20,2) | YES | | Market value of equity = price * shares_outstanding | Computed in ETL |
| dividend_cash_paid | decimal(20,2) | YES | | Dividend payment (cash) | Market/FS notes |
| eps_basic | decimal(20,6) | YES | | Earnings per share | Market/FS |
| currency_code | char(3) | NO | | Currency code | Default VND |
| created_at | timestamp | YES | | Row creation timestamp | Auto |

### fact_ownership_year

| Column Name | Data Type | Nullable | Key | Description | Source/Rule |
|-------------|-----------|----------|-----|-------------|-------------|
| firm_id | bigint | NO | PK, FK | Firm identifier | FK -> dim_firm(firm_id) |
| fiscal_year | smallint | NO | PK | Fiscal year | Year column in panel |
| snapshot_id | bigint | NO | PK, FK | Snapshot/version link | FK -> fact_data_snapshot(snapshot_id) |
| managerial_inside_own | decimal(20,6) | YES | | Fraction owned by BOD/management (0..1) | FiinPro/ownership report |
| state_own | decimal(20,6) | YES | | Fraction owned by government (0..1) | FiinPro/ownership report |
| institutional_own | decimal(20,6) | YES | | Fraction owned by domestic institutions (0..1) | FiinPro/ownership report |
| foreign_own | decimal(20,6) | YES | | Fraction owned by foreign investors (0..1) | FiinPro/ownership report |
| note | varchar(255) | YES | | ETL notes/caveats | ETL |
| created_at | timestamp | YES | | Row creation timestamp | Auto |

### fact_innovation_year

| Column Name | Data Type | Nullable | Key | Description | Source/Rule |
|-------------|-----------|----------|-----|-------------|-------------|
| firm_id | bigint | NO | PK, FK | Firm identifier | FK -> dim_firm(firm_id) |
| fiscal_year | smallint | NO | PK | Fiscal year | Year column in panel |
| snapshot_id | bigint | NO | PK, FK | Snapshot/version link | FK -> fact_data_snapshot(snapshot_id) |
| product_innovation | tinyint | YES | | Dummy: announced new product (0/1) | Annual report / disclosure coding rules |
| process_innovation | tinyint | YES | | Dummy: announced new process (0/1) | Annual report / disclosure coding rules |
| evidence_source_id | smallint | YES | FK | Source supporting innovation dummy | FK -> dim_data_source(source_id) |
| evidence_note | varchar(500) | YES | | Evidence note (URL/page/quote pointer) | Analyst annotation |
| created_at | timestamp | YES | | Row creation timestamp | Auto |

### fact_firm_year_meta

| Column Name | Data Type | Nullable | Key | Description | Source/Rule |
|-------------|-----------|----------|-----|-------------|-------------|
| firm_id | bigint | NO | PK, FK | Firm identifier | FK -> dim_firm(firm_id) |
| fiscal_year | smallint | NO | PK | Fiscal year | Year column in panel |
| snapshot_id | bigint | NO | PK, FK | Snapshot/version link | FK -> fact_data_snapshot(snapshot_id) |
| employees_count | int | YES | | Number of employees | Annual report / sustainability report |
| firm_age | smallint | YES | | Firm age in years at fiscal_year | Rule: fiscal_year - founded_year + 1 (or study rule) |
| created_at | timestamp | YES | | Row creation timestamp | Auto |

### fact_value_override_log

| Column Name | Data Type | Nullable | Key | Description | Source/Rule |
|-------------|-----------|----------|-----|-------------|-------------|
| override_id | bigint | NO | PK | Audit key for overrides | Auto increment |
| firm_id | bigint | NO | FK | Firm identifier | FK -> dim_firm(firm_id) |
| fiscal_year | smallint | NO | | Fiscal year | Year column in panel |
| table_name | varchar(80) | NO | | Target table of override | ETL/data cleaning |
| column_name | varchar(80) | NO | | Target column of override | ETL/data cleaning |
| old_value | varchar(255) | YES | | Old value as text (for audit) | Captured from prior fact row |
| new_value | varchar(255) | YES | | New value as text | Analyst corrected value |
| reason | varchar(255) | YES | | Reason for override | Data quality note |
| changed_by | varchar(80) | YES | | User/bot making change | ETL user/bot |
| changed_at | timestamp | YES | | When override logged | Auto |

## 4. Table Relationships

| From Table | From Column | To Table | To Column | Cardinality | Note |
|------------|-------------|----------|-----------|-------------|------|
| dim_firm | exchange_id | dim_exchange | exchange_id | N:1 | Each firm belongs to one exchange |
| dim_firm | industry_l2_id | dim_industry_l2 | industry_l2_id | N:1 | Each firm may belong to one L2 industry |
| fact_data_snapshot | source_id | dim_data_source | source_id | N:1 | Each snapshot comes from one source |
| fact_ownership_year | firm_id | dim_firm | firm_id | N:1 | Ownership panel by firm |
| fact_ownership_year | snapshot_id | fact_data_snapshot | snapshot_id | N:1 | Ownership values tied to snapshot/version |
| fact_financial_year | firm_id | dim_firm | firm_id | N:1 | Financial panel by firm |
| fact_financial_year | snapshot_id | fact_data_snapshot | snapshot_id | N:1 | Financial values tied to snapshot/version |
| fact_cashflow_year | snapshot_id | fact_data_snapshot | snapshot_id | N:1 | Cashflow tied to snapshot/version |
| fact_market_year | snapshot_id | fact_data_snapshot | snapshot_id | N:1 | Market data tied to snapshot/version |
| fact_innovation_year | snapshot_id | fact_data_snapshot | snapshot_id | N:1 | Innovation coding tied to snapshot/version |
| fact_innovation_year | evidence_source_id | dim_data_source | source_id | N:1 | Evidence source for dummy variables |
| fact_firm_year_meta | snapshot_id | fact_data_snapshot | snapshot_id | N:1 | Employees/age tied to snapshot/version |
